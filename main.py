import cv2
from cvzone.HandTrackingModule import HandDetector
import serial
import time
import numpy as np

# Initialize webcam
cap = cv2.VideoCapture(0)

# Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Serial connection
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

# Finger landmarks
INDEX_TIP = 8
PALM_BASE = 0  # Wrist point for reference

# Coordinate system parameters
SCALE_FACTOR = 0.5  # Adjust sensitivity
DEADZONE_RADIUS = 15  # Pixels

# Reference positions
ref_pos = None
current_motor_pos = 512  # Midpoint (0-1023 range)


def send_motor_position(pos):
    """Send position to Arduino (0-1023)"""
    pos = max(0, min(1023, int(pos)))
    arduino.write(f"{pos}\n".encode())
    return pos


while True:
    success, img = cap.read()
    if not success:
        break

    hands, img = detector.findHands(img, flipType=True)

    if hands:
        hand = hands[0]

        if hand["type"] == "Right":
            lmList = hand["lmList"]

            # Get current finger and palm positions
            tip_pos = np.array(lmList[INDEX_TIP][:2])
            palm_base = np.array(lmList[PALM_BASE][:2])

            # Initialize reference on first detection
            if ref_pos is None:
                ref_pos = tip_pos.copy()

            # Calculate movement vector from reference
            movement = tip_pos - ref_pos
            distance = np.linalg.norm(movement)

            # Only update if outside deadzone
            if distance > DEADZONE_RADIUS:
                # Normalize and scale movement
                direction = movement / distance
                position_change = (movement * SCALE_FACTOR).astype(int)

                # Update motor position
                current_motor_pos = send_motor_position(
                    current_motor_pos + position_change[1])  # Using Y-axis for vertical control

                # Update reference position (elastic anchor)
                ref_pos = tip_pos - (direction * DEADZONE_RADIUS)

            # Visual feedback
            cv2.circle(img, tuple(ref_pos.astype(int)), 10, (0, 255, 0), -1)
            cv2.circle(img, tuple(tip_pos.astype(int)), 8, (255, 0, 0), -1)
            cv2.line(img, tuple(ref_pos.astype(int)), tuple(tip_pos.astype(int)), (0, 0, 255), 2)
            cv2.putText(img, f"Motor Pos: {current_motor_pos}", (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Position Control", img)
    if cv2.waitKey(1) == 27:
        break

# Reset motor to center on exit
send_motor_position(512)
cap.release()
cv2.destroyAllWindows()
arduino.close()