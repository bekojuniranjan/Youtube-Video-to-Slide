from pytube import YouTube
import cv2
import numpy as np
from PIL import Image as im 
from sklearn.neighbors import LocalOutlierFactor
import streamlit as st
import asyncio
import base64

class YouTubetoSlide:

    def __init__(self) -> None:
        self.download_dir = "youtube-download"
        self.slide_dir = "youtube-slide"

    def download_youtube_video(self, link):
        link = link.split("&")[0]
        yt = YouTube(link)
        try:
            self.title = yt.title.split()[0] + ".mp4"
        except:
            self.title = "current_video.mp4"    
        print(self.title)
        try:
            print("Downloding Video...")
            try:
                yt.streams.filter(adaptive=True, only_video=True).order_by('resolution').desc().first().download(self.download_dir, self.title)
                print("Download Completed")
            except KeyError as e:
                yt.streams.filter(progressive=True).order_by('resolution').desc().first().download(self.download_dir, self.title)
                print("Download Completed")
        except AttributeError as ae:
            print("Attribute Error try another video")
            st.write("Attribute Error \n try with another video url")


    def read_frame_and_cal_diff(self, skip_sec = 2):
        cap = cv2.VideoCapture(self.download_dir + "/" + self.title)

        if (cap.isOpened() == False):
            print("Error opening video file")

        self.list_of_frame = []
        previous_Frame = None
        self.diff_values = []
        frame_count = 0
        fps = cap.get(cv2.CAP_PROP_FPS)
        while(cap.isOpened()):
            frame_id = int(fps*(skip_sec * frame_count))
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
            ret, frame = cap.read()
            if ret:
                if previous_Frame is not None:
                    h, w, _ = frame.shape
                    diff = cv2.subtract(frame, previous_Frame)
                    diff_value  = np.sum(diff) / (h * w)
                    # print(diff_value, frame_count, frame_id)
                    self.diff_values.append(diff_value)
                previous_Frame = frame
                self.list_of_frame.append(frame)
                frame_count += 1 
            else:
                cap.release()
                break
    
    def get_appropriate_frame_and_make_pdf(self):
        # predicting slides using Thresholding values

        list_of_frame_arr = np.array(self.list_of_frame)
        frames_for_slide = list_of_frame_arr[np.where(np.array(self.diff_values) > 10)[0]]
        images = []
        for i in range(frames_for_slide.shape[0]):
            img_arr = frames_for_slide[i]
            img_arr = cv2.cvtColor(img_arr, cv2.COLOR_BGR2RGB)
            images.append(im.fromarray(img_arr))
        self.file_path = self.slide_dir + "/" + self.title.split('.')[0]+".pdf"
        images[0].save(self.file_path, save_all=True, append_images = images[1:])
        st.write("Get PDF at " + self.file_path)

    def show_pdf(self):
        pass
        # with open(self.file_path,"rb") as f:
        #     base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        # pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'
        # st.markdown(pdf_display, unsafe_allow_html=True)

    async def start_process(self, link, skip_sec):
        self.download_youtube_video(link=link)
        self.read_frame_and_cal_diff(skip_sec=skip_sec)
        self.get_appropriate_frame_and_make_pdf()
        # self.show_pdf()


if __name__ == "__main__":
    st.header('YouTube Video to Slide Converter')
    link = st.text_input('**YouTube Link** (Add your YouTube Video Link Here)', "https://www.youtube.com/watch?v=OkbCAljWbHI&t=19s&ab_channel=edureka%21")
    skip_sec = st.slider('Skip Seconds',1,10,3)

    youtube = YouTubetoSlide()
    asyncio.run(youtube.start_process(link, skip_sec))
