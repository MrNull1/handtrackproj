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
# Python Code (Modified)
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

                # Dictionary to store finger distances
                finger_distances = {}

                # List of finger landmarks to process (INDEX, MIDDLE, RING, PINKY)
                fingers = [
                    (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP),
                    (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP),
                    (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_MCP),
                    (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_MCP)
                ]

                for i, (tip, base) in enumerate(fingers):
                    tip_pos = hand_landmarks.landmark[tip]
                    base_pos = hand_landmarks.landmark[base]

                    # Calculate vertical difference
                    finger_distance = tip_pos.y - base_pos.y

                    # Factor in depth (distance from the camera)
                    depth = tip_pos.z
                    adjusted_distance = finger_distance / (abs(depth) + 1)  # Normalize by depth
                    adjusted_distance *= 25
                    adjusted_distance = int(adjusted_distance)
                    finger_distances[f"finger_{i + 1}"] = adjusted_distance

                # Send finger distances to Arduino as a comma-separated string
                serial_data = ",".join([str(v) for v in finger_distances.values()])
                ser.write(f"{serial_data}\n".encode())
                print(serial_data)

    cv2.imshow("Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()
