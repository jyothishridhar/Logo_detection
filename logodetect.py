import cv2
from openpyxl import Workbook
import streamlit as st
from tempfile import NamedTemporaryFile
import os

def run_logo_detection(logo_path, video_path):
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

        # Break the loop if 'q' is pressed
        if st.button("Stop Detection"):
            break

    # Save the Excel workbook
    report_path = 'C:\\OTT_Logo_detect\\logo_detection_report.xlsx'  # Path to save the Excel report
    workbook.save(report_path)
    return report_path  # Return the path for downloading

# Streamlit app code
st.title("Logo Detection Demo")

logo_path = st.file_uploader("Upload Logo Image", type=["png", "jpg", "jpeg"])
video_path = st.file_uploader("Upload Video File", type=["mp4"])

if st.button("Run Demo"):
    if logo_path is not None and video_path is not None:
        # Save the logo and video locally
        with NamedTemporaryFile(delete=False, suffix=".png") as temp_logo:
            temp_logo.write(logo_path.read())
            logo_path = temp_logo.name

        with NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            temp_video.write(video_path.read())
            video_path = temp_video.name

        result_path = run_logo_detection(logo_path, video_path)

        # Display the result and provide a download link
        st.success(f"Demo completed! Result saved to: {result_path}")
        st.download_button("Download Result", result_path, key="result_download")

        # Clean up temporary files
        os.unlink(logo_path)
        os.unlink(video_path)
    else:
        st.warning("Please upload both the logo and video files.")

st.text("Note: This is a simplified example. Adjust the paths and parameters as needed.")
