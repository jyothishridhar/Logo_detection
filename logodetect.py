import cv2
from openpyxl import Workbook
import streamlit as st
import os
import numpy as np
import tempfile
import pandas as pd
import requests
import shutil  # Import the shutil module for copying files

def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    with open(dest_path, 'wb') as file:
        shutil.copyfileobj(response.raw, file)

def run_logo_detection(logo_path, video_path, stop_flag):
    st.write("Starting logo detection...")

    # Download the logo image
    logo_dest_path = "logo.png"
    download_file(logo_path, logo_dest_path)

    # Read the logo image from the file
    logo = cv2.imread(logo_dest_path)
    gray_logo = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    keypoints_logo, descriptors_logo = sift.detectAndCompute(gray_logo, None)

    # Save the video file locally
    video_dest_path = "video.mp4"
    download_file(video_path, video_dest_path)

    # Open the locally saved video file
    cap = cv2.VideoCapture(video_dest_path)
    frame_number = 0
    # Lists to store frame numbers and detection status
    frame_numbers = []
    detection_statuses = []

    while cap.isOpened():
        # Rest of the code remains unchanged

# Streamlit app code
st.title("Logo Detection Demo")

# Git LFS URLs for the videos
logo_url = "https://github.com/jyothishridhar/Logo_detection/raw/master/zee5_logo.png"
video_url = "https://github.com/jyothishridhar/Logo_detection/raw/master/concatenate_zee.mp4"

# Add download links for the logo and video
st.markdown(f"**Download Logo Image**")
st.markdown(f"[Click here to download the Logo Image]({logo_url})")

st.markdown(f"**Download Reference Video**")
st.markdown(f"[Click here to download the Reference Video]({video_url})")

logo_path = "logo.png"  # Use a fixed file path for logo
video_path = "video.mp4"  # Use a fixed file path for the video
stop_flag = [False]  # Using a list to make it mutable

if st.button("Run Demo"):
    result_df = run_logo_detection(logo_path, video_path, stop_flag)
    # Rest of the code remains unchanged
