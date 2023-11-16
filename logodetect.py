import cv2
from openpyxl import Workbook
import streamlit as st
import os
import numpy as np
from io import BytesIO
import base64
import tempfile

def run_logo_detection(logo_path, video_path, stop_flag):
    print("Starting logo detection...")

    # Read the logo image from the file uploader
    logo = cv2.imdecode(np.frombuffer(logo_path.read(), np.uint8), cv2.IMREAD_COLOR)
    gray_logo = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    keypoints_logo, descriptors_logo = sift.detectAndCompute(gray_logo, None)

    # Save the video file locally
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(video_path.read())
        video_path = temp_video.name

    # Open the locally saved video file
    cap = cv2.VideoCapture(video_path)
    frame_number = 0

    # Create an Excel workbook and sheet
    workbook = Workbook()
    sheet = workbook.active

    # Write headers to the sheet
    sheet['A1'] = 'Frame Number'
    sheet['B1'] = 'Logo Detection Status'
    row = 2  # Start from the second row for data

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1  # Increment the frame number

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

        print(f"Frame: {frame_number}, Good Matches: {len(good_matches)}")

        # If enough good matches are found, consider the logo is detected
        if len(good_matches) > 10:  # Adjust the threshold value as per your requirement
            logo_detected = True
            detection_status = 'Logo Detected'
        else:
            logo_detected = False
            detection_status = 'Logo Not Detected'

        # Write the frame number and logo detection status to the Excel sheet
        sheet[f'A{row}'] = frame_number
        sheet[f'B{row}'] = detection_status
        row += 1  # Increment the row

        # Check the stop_flag to stop detection
        if stop_flag[0]:
            break

    # Save the Excel workbook to a BytesIO object
    result_file = BytesIO()
    workbook.save(result_file)

    # Clean up the temporary video file
    os.unlink(video_path)

    print("Logo detection completed.")
    return result_file, sheet

# Streamlit app code
st.title("Logo Detection Demo")

logo_path = st.file_uploader("Upload Logo Image", type=["png", "jpg", "jpeg"])
video_path = st.file_uploader("Upload Video File", type=["mp4"])

stop_flag = [False]  # Using a list to make it mutable

if st.button("Run Demo"):
    if logo_path is not None and video_path is not None:
        result_file, sheet = run_logo_detection(logo_path, video_path, stop_flag)

        # Display the result on the app
        st.success("Demo completed! Result:")

        # Display the DataFrame
        st.write(sheet)

        # Create a download button for the Excel file
        if st.button("Download Result"):
            st.markdown(f"Download the result: [logo_detection_report.xlsx](data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{base64.b64encode(result_file.getvalue()).decode()})")

        # Clean up
        result_file.close()
    else:
        st.warning("Please upload both the logo and video files.")
