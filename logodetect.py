import cv2
from openpyxl import Workbook
import streamlit as st
import os
import numpy as np

def run_logo_detection(logo_path, video_path, stop_flag, report_path_placeholder):
    print("Starting logo detection...")
    logo = cv2.imread(logo_path)
    gray_logo = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
    sift = cv2.SIFT_create()
    keypoints_logo, descriptors_logo = sift.detectAndCompute(gray_logo, None)

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

    # Save the Excel workbook
    report_filename = 'logo_detection_report.xlsx'
    result_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), report_filename)
    workbook.save(result_path)  # Save in the script's directory

    # Update the placeholder content
    report_path_placeholder.markdown(f"Download the result: [logo_detection_report.xlsx]({result_path})")

    print("Logo detection completed.")
    return result_path

# Streamlit app code
st.title("Logo Detection Demo")

logo_path = st.file_uploader("Upload Logo Image", type=["png", "jpg", "jpeg"])
video_path = st.file_uploader("Upload Video File", type=["mp4"])

stop_flag = [False]  # Using a list to make it mutable

if st.button("Run Demo"):
    if logo_path is not None and video_path is not None:
        # Convert the logo and video to temporary images
        temp_logo = cv2.imencode('.png', np.frombuffer(logo_path.read(), np.uint8))[1].tostring()
        temp_video = cv2.imencode('.mp4', np.frombuffer(video_path.read(), np.uint8))[1].tostring()

        # Save the logo and video locally
        with open("temp_logo.png", "wb") as f:
            f.write(temp_logo)

        with open("temp_video.mp4", "wb") as f:
            f.write(temp_video)

        # Specify the directory to save the report
        report_filename = 'logo_detection_report.xlsx'
        result_path = os.path.join(os.getcwd(), report_filename)

        # Create a placeholder for the report path
        report_path_placeholder = st.empty()

        result_path = run_logo_detection("temp_logo.png", "temp_video.mp4", stop_flag, report_path_placeholder)

        # Display the result and provide a download link
        st.success(f"Demo completed! Result saved to: {result_path}")

        # Clean up temporary files
        os.unlink("temp_logo.png")
        os.unlink("temp_video.mp4")
    else:
        st.warning("Please upload both the logo and video files.")
