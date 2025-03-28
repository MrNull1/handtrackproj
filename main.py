import cv2
from cvzone.HandTrackingModule import HandDetector

# Initialize the webcam
webcam = cv2.VideoCapture(0)

# Initialize the Hand Tracker
hand_detector = HandDetector(detectionCon=0.8, maxHands=1)

# Get the screen resolution
screen_width = 1920  # Replace with your screen width
screen_height = 1080  # Replace with your screen height

# Create a named window and set it to fullscreen
cv2.namedWindow("Hand Tracking - AI", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("Hand Tracking - AI", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    # Capture the image from the webcam
    success, img = webcam.read()

    if not success:
        print("Failed to capture image from the webcam.")
        break

    # Detect hands in the frame
    hands, img_hands = hand_detector.findHands(img)

    # Resize the image to fit the screen resolution
    img_resized = cv2.resize(img_hands, (screen_width, screen_height))

    # Display the frame with annotations
    cv2.imshow("Hand Tracking - AI", img_resized)

    # Exit the application only when the Escape key is pressed
    if cv2.waitKey(1) == 27:  # 27 is the key code for the Escape key
        break

# Release the webcam and close the windows
webcam.release()
cv2.destroyAllWindows()
