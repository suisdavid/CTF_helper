import cv2
import numpy as np
import os

cap = cv2.VideoCapture("static.mp4")
os.makedirs("recovered", exist_ok=True)

binary_frames = []

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)

    binary_frames.append(binary)

cap.release()

for i in range(2, len(binary_frames)):
    current = binary_frames[i]
    previous = binary_frames[i - 2]

    # 相同位置设为白色，不同位置设为黑色
    same = np.where(current == previous, 255, 0).astype(np.uint8)

    cv2.imwrite(f"recovered/frame_{i:05d}.png", same)
