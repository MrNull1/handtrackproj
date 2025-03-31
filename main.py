import cv2
import mediapipe as mp
import serial
import time
import numpy as np

# Set up serial communication with Arduino
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)  # Faster baud rate
time.sleep(2)  # Allow time for connection

# Initialize MediaPipe Hand Tracking
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# OpenCV video capture
cap = cv2.VideoCapture(0)

prev_value = 0  # Track previous finger position
last_sent_time = time.time()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Mirror the frame
    h, w, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get index finger tip and base positions
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            index_base = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]

            # Calculate vertical difference
            finger_distance = index_tip.y - index_base.y

            # Map to range (-500 to 500) for smooth motion
            motor_value = int(np.clip(finger_distance * -1000, -500, 500))

            # Send only if there's a significant change & not too frequent
            if abs(motor_value - prev_value) > 5 and (time.time() - last_sent_time) > 0.05:
                ser.write(f"{motor_value}\n".encode())
                prev_value = motor_value
                last_sent_time = time.time()

    cv2.imshow("Hand Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
ser.close()
