import cv2
from openpyxl import Workbook
import streamlit as st
import os
import numpy as np
import tempfile
import pandas as pd
import requests
from io import BytesIO

def download_image(url):
    response = requests.get(url)
    return BytesIO(response.content)

def download_video(url):
    response = requests.get(url)
    return BytesIO(response.content)

def run_logo_detection(logo_path, video_path, stop_flag):
    st.write("Starting logo detection...")

    # Read the logo image from the website
    logo_bytes = download_image(logo_path)
    logo_np = np.frombuffer(logo_bytes.getvalue(), np.uint8)
    logo = cv2.imdecode(logo_np, cv2.IMREAD_COLOR)

    # Convert logo to grayscale
    gray_logo = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)

    # Initialize ORB detector
    orb = cv2.ORB_create()

    # Find the keypoints and descriptors with ORB
    keypoints_logo, descriptors_logo = orb.detectAndCompute(gray_logo, None)

    # Read the video file from the website
    video_bytes = download_video(video_path)

    # Save the video file locally
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_bytes.getvalue())
        video_path = temp_video.name

    # Open the locally saved video file
    cap = cv2.VideoCapture(video_path)
    frame_number = 0

    # Lists to store frame numbers and detection status
    frame_numbers = []
    detection_statuses = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1  # Increment the frame number

        # Convert the frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Initialize ORB detector
        keypoints_frame, descriptors_frame = orb.detectAndCompute(gray_frame, None)

        # Match the descriptors between the logo and the frame using BFMatcher
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = matcher.match(descriptors_logo, descriptors_frame)

        # Sort the matches by their distances
        matches = sorted(matches, key=lambda x: x.distance)

        # Define a threshold to filter out the matches
        threshold = 30  # Adjust the threshold value as per your requirement

        # Filter out the good matches based on the threshold
        good_matches = [match for match in matches if match.distance < threshold]

        st.write(f"Frame: {frame_number}, Good Matches: {len(good_matches)}")

        # If enough good matches are found, consider the logo is detected
        if len(good_matches) > 10:  # Adjust the threshold value as per your requirement
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

logo_path = "https://github.com/jyothishridhar/Logo_detection/raw/master/zee5_logo.png"
video_path = "https://github.com/jyothishridhar/Logo_detection/raw/master/concatenate_zee.mp4"

stop_flag = [False]  # Using a list to make it mutable

if st.button("Run Demo"):
    result_df = run_logo_detection(logo_path, video_path, stop_flag)

    # Display the result on the app
    st.success("Demo completed! Result:")

    # Display the DataFrame
    st.dataframe(result_df)
