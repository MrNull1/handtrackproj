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

# Calibration variables
calibration_mode = False
selected_finger = 0  # 0: Index, 1: Middle, 2: Ring, 3: Pinky
step_amount = 0  # Step amount for adjustment
finger_names = ["Index", "Middle", "Ring", "Pinky"]

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror the frame
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks and result.multi_handedness:
        # Regular Tracking Mode
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

    if calibration_mode:
        # Overlay calibration mode info on the video feed
        cv2.putText(frame, f"Calibration Mode: ON", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Selected Finger: {finger_names[selected_finger]}", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Step Amount: {step_amount}", 
                    (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    cv2.imshow("Live Video Feed", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):  # Quit program
        break
    elif key == ord('t'):  # Toggle calibration mode
        calibration_mode = not calibration_mode
    elif calibration_mode:
        # Handle calibration commands
        if key in [ord('1'), ord('2'), ord('3'), ord('4')]:  # Select finger
            selected_finger = key - ord('1')
        elif key == ord('+'):  # Increase step amount
            step_amount += 1
        elif key == ord('-'):  # Decrease step amount
            step_amount -= 1
        elif key == ord('c'):  # Send calibration data
            command = f"{selected_finger},{step_amount}"
            ser.write(f"{command}\n".encode())
            print(f"Sent Calibration Command to Arduino: {command}")

cap.release()
cv2.destroyAllWindows()
ser.close()
