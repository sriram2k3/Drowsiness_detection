# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kwnfGVldwJ-ws2OzKwLAv-a43fwbhji5
"""

!pip install pyttsx3

import cv2
import dlib
import pyttsx3
from scipy.spatial import distance
from IPython.display import display, Javascript
from google.colab.output import eval_js
from base64 import b64decode
from ipywidgets import Image
import io

# Initialize pyttsx3 for audio alerts
!apt-get install libespeak1
engine = pyttsx3.init()

# Load face detector and facial landmark predictor
face_detector = dlib.get_frontal_face_detector()
!wget -O shape_predictor_68_face_landmarks.dat "https://drive.google.com/uc?id=1r4FaTkYHbR0qaU2fMJ7XLFakk1SqlxOV"

dlib_facelandmark = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Function to calculate eye aspect ratio
def Detect_Eye(eye):
    poi_A = distance.euclidean(eye[1], eye[5])
    poi_B = distance.euclidean(eye[2], eye[4])
    poi_C = distance.euclidean(eye[0], eye[3])
    aspect_ratio_Eye = (poi_A + poi_B) / (2 * poi_C)
    return aspect_ratio_Eye

# Function to capture photo using JavaScript
def take_photo(filename='photo.jpg', quality=0.8):
    js = Javascript('''
        async function takePhoto(quality) {
            const div = document.createElement('div');
            const capture = document.createElement('button');
            capture.textContent = 'Capture';
            div.appendChild(capture);

            const video = document.createElement('video');
            video.style.display = 'block';
            const stream = await navigator.mediaDevices.getUserMedia({video: true});

            document.body.appendChild(div);
            div.appendChild(video);
            video.srcObject = stream;
            await video.play();

            // Resize the output to fit the video element.
            google.colab.output.setIframeHeight(document.documentElement.scrollHeight, true);

            // Capture a frame when the "Capture" button is clicked.
            await new Promise((resolve) => capture.onclick = resolve);

            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            stream.getVideoTracks()[0].stop();
            div.remove();
            return canvas.toDataURL('image/jpeg', quality);
        }
    ''')
    display(js)
    # Get the photo data
    data = eval_js('takePhoto({})'.format(quality))
    binary = b64decode(data.split(',')[1])

    # Write the photo to the file.
    with open(filename, 'wb') as f:
        f.write(binary)

    return filename

# Create an Image widget
image_widget = Image()

# Main loop
while True:
    # Capture photo
    take_photo('photo.jpg')

    # Read the captured photo
    frame = cv2.imread('photo.jpg')

    # Convert the frame to grayscale
    gray_scale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = face_detector(gray_scale)

    for face in faces:
        # Get the face landmarks
        face_landmarks = dlib_facelandmark(gray_scale, face)
        leftEye = []
        rightEye = []

        # Extract left and right eye coordinates
        for n in range(42, 48):
            x = face_landmarks.part(n).x
            y = face_landmarks.part(n).y
            rightEye.append((x, y))
            next_point = n+1
            if n == 47:
                next_point = 42
            x2 = face_landmarks.part(next_point).x
            y2 = face_landmarks.part(next_point).y
            cv2.line(frame, (x, y), (x2, y2), (0, 255, 0), 1)

        for n in range(36, 42):
            x = face_landmarks.part(n).x
            y = face_landmarks.part(n).y
            leftEye.append((x, y))
            next_point = n+1
            if n == 41:
                next_point = 36
            x2 = face_landmarks.part(next_point).x
            y2 = face_landmarks.part(next_point).y
            cv2.line(frame, (x, y), (x2, y2), (255, 255, 0), 1)

        # Calculate the aspect ratio for left and right eye
        right_Eye = Detect_Eye(rightEye)
        left_Eye = Detect_Eye(leftEye)
        Eye_Rat = (left_Eye+right_Eye)/2

        # This value of 0.25 (you can even change it)
        # will decide whether the person's eyes are close or not
        if Eye_Rat < 0.25:
            print("ALERT : DROWSINESS DETECTED")
            engine.say("Eyes are closed")
            engine.runAndWait()
        else:
            print("0 - DROWSINESS NOT DETECTED")

# Release the camera and close all OpenCV windows
cv2.destroyAllWindows()

