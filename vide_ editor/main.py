import cv2
import numpy as np

def on_trackbar(val):
    pass


cv2.namedWindow('Video', cv2.WINDOW_AUTOSIZE)
cv2.namedWindow('Configuration', cv2.WINDOW_AUTOSIZE)
cv2.resizeWindow('Configuration', 500, 500)

cv2.createTrackbar('Record', 'Configuration', 0, 1, on_trackbar)
cv2.createTrackbar('Brightness', 'Configuration', 0, 3, on_trackbar)
cv2.createTrackbar('GaussianBlur', 'Configuration', 0, 1, on_trackbar)
cv2.createTrackbar('Cut', 'Configuration', 0, 1, on_trackbar)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Could not open camera")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi', fourcc, 15, (width, height))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    processed_frame = frame.copy()

    processed_frame = cv2.resize(processed_frame, (1600, 900))

    # Яркость
    brightness = cv2.getTrackbarPos('Brightness', 'Configuration')
    if brightness == 1:
        processed_frame = cv2.convertScaleAbs(processed_frame, alpha=1.8, beta=0)
    elif brightness == 2:
        processed_frame = cv2.convertScaleAbs(processed_frame, alpha=2.5, beta=0)
    elif brightness == 3:
        processed_frame = cv2.convertScaleAbs(processed_frame, alpha=3.0, beta=0)

    if cv2.getTrackbarPos('GaussianBlur', 'Configuration'):
        processed_frame = cv2.GaussianBlur(processed_frame, (25, 25), 0)

    if cv2.getTrackbarPos('Cut', 'Configuration'):
        x, y, w, h = 240, 50, 250, 250
        processed_frame = processed_frame[y:y + h, x:x + w]

    cv2.imshow('Video', processed_frame)

    if cv2.getTrackbarPos('Record', 'Configuration'):
        if processed_frame.shape[:2] != (height, width):
            resized_frame = cv2.resize(processed_frame, (width, height))
            out.write(resized_frame)
        else:
            out.write(processed_frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
out.release()
cv2.destroyAllWindows()