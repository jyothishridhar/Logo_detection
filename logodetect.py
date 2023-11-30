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
        ret, frame = cap.read()
        if not ret:
            break
        frame_number += 1 # Increment the frame number
        # Convert the frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Initialize the SIFT detector and compute the keypoints and descriptors for the frame
        keypoints_frame, descriptors_frame = sift.detectAndCompute(gray_frame, None)
        # Match the descriptors between the logo and the frame
        matcher = cv2.BFMatcher()
        matches = matcher.match(descriptors_logo, descriptors_frame)
        # Sort the matches by their distance
        matches = sorted(matches, key=lambda x: x.distance)
        # Define a threshold to filter out the matches
        threshold = 0.7
        # Filter out the good matches based on the threshold
        good_matches = [match for match in matches if match.distance < threshold * len(matches)]
        st.write(f"Frame: {frame_number}, Good Matches: {len(good_matches)}")
        # If enough good matches are found, consider the logo is detected
        if len(good_matches) > 10: # Adjust the threshold value as per your requirement
            logo_detected = True
            detection_status = 'Logo Detected'
        else:
            logo_detected = False
            detection_status = 'Logo Not Detected'
        # Append frame number and detection status to the lists
        frame_numbers.append(frame_number)
        detection_statuses.append(detection_status)
        # Display the frame with logo detection status and frame number
        st.image(frame, channels="BGR")
        st.write(f'Detection Status: {detection_status}, Frame: {frame_number}')
        # Check the stop_flag to stop detection
        if stop_flag[0]:
            break
    # Save the Excel workbook
    result_df = pd.DataFrame({'Frame Number': frame_numbers, 'Logo Detection Status': detection_statuses})
    result_path = os.path.join(os.getcwd(), "logo_detection_report.xlsx")
    result_df.to_excel(result_path, index=False)
    # Clean up the temporary video file
    os.unlink(video_path)
    st.write("Logo detection completed.")
    return result_df
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
    # Display the result on the app
    st.success("Demo completed! Result:")
 # Display the DataFrame
    st.dataframe(result_df)
else:
    st.warning("Please upload both the logo and video files.")

