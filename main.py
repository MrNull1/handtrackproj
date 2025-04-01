import cv2
import mediapipe as mp
import serial
import time
import numpy as np
from math import floor

# Set up serial communication with Arduino
ser = serial.Serial('/dev/cu.usbmodem1201', 115200, timeout=1)  # Faster baud rate
time.sleep(2)  # Allow time for connection

# Initialize MediaPipe Hand Tracking
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=1)

# OpenCV video capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror the frame
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks and result.multi_handedness:
        for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            if handedness.classification[0].label == 'Right':  # Process only the right hand
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Get index finger tip and base positions
                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
                index_base = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y

                # Calculate vertical difference
                finger_distance = index_tip - index_base
                finger_distance *= 25
                finger_distance = int(finger_distance)
                print(finger_distance)

                # Send finger distance to Arduino
                ser.write(f"{finger_distance}\n".encode())

    cv2.imshow("Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()
