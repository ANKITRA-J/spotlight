# spotlight_core.py
import cv2
import numpy as np


class Spotlight:
    def __init__(self):
        self.cap = None
    
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # smoothing
        self.prev_box = None
        self.smooth_factor = 0.3

        # Frame parameters
        self.frame_width = 640
        self.frame_height = 480
        self.last_valid_frame = None

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam")

    def smooth_box(self, current_box):
        if self.prev_box is None:
            self.prev_box = current_box
            return current_box

        # linear interpolation
        x1, y1, w1, h1 = self.prev_box
        x2, y2, w2, h2 = current_box

        smooth_x = int(x1 + (x2 - x1) * self.smooth_factor)
        smooth_y = int(y1 + (y2 - y1) * self.smooth_factor)
        smooth_w = int(w1 + (w2 - w1) * self.smooth_factor)
        smooth_h = int(h1 + (h2 - h1) * self.smooth_factor)

        self.prev_box = (smooth_x, smooth_y, smooth_w, smooth_h)
        return self.prev_box

    def get_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return self.last_valid_frame if self.last_valid_frame is not None else None

        ret, frame = self.cap.read()
        if not ret:
            return self.last_valid_frame if self.last_valid_frame is not None else None

        # for mirror effect
        frame = cv2.flip(frame, 1)

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces with relaxed parameters
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.3,
            minNeighbors=4,
            minSize=(30, 30)
        )

        if len(faces) > 0:
            # Get the largest face
            face_box = max(faces, key=lambda box: box[2] * box[3])

            # Apply smoothing
            x, y, w, h = self.smooth_box(face_box)

            # Calculate crop region with fixed scale
            crop_scale = 1.8
            crop_size = int(max(w, h) * crop_scale)

            # Calculate center point
            cx = x + w // 2
            cy = y + h // 2

            # Calculate crop bounds
            x1 = max(cx - crop_size // 2, 0)
            y1 = max(cy - crop_size // 2, 0)
            x2 = min(cx + crop_size // 2, frame.shape[1])
            y2 = min(cy + crop_size // 2, frame.shape[0])

            # Ensure minimum crop size
            if x2 - x1 > 0 and y2 - y1 > 0:
                # Crop and resize
                cropped = frame[y1:y2, x1:x2]
                if cropped.size > 0:
                    frame = cv2.resize(cropped, (self.frame_width, self.frame_height))

                    # Draw debug rectangle
                    face_x = int((x - x1) * self.frame_width / (x2 - x1))
                    face_y = int((y - y1) * self.frame_height / (y2 - y1))
                    face_w = int(w * self.frame_width / (x2 - x1))
                    face_h = int(h * self.frame_height / (y2 - y1))
                    cv2.rectangle(frame, (face_x, face_y),
                                  (face_x + face_w, face_y + face_h),
                                  (0, 255, 0), 2)
        elif self.prev_box is not None:
            # Use last known position with a bit larger crop
            x, y, w, h = self.prev_box
            crop_scale = 2.0  # Slightly larger crop when face is lost
            crop_size = int(max(w, h) * crop_scale)

            cx = x + w // 2
            cy = y + h // 2

            x1 = max(cx - crop_size // 2, 0)
            y1 = max(cy - crop_size // 2, 0)
            x2 = min(cx + crop_size // 2, frame.shape[1])
            y2 = min(cy + crop_size // 2, frame.shape[0])

            if x2 - x1 > 0 and y2 - y1 > 0:
                cropped = frame[y1:y2, x1:x2]
                if cropped.size > 0:
                    frame = cv2.resize(cropped, (self.frame_width, self.frame_height))

        # Convert to RGB for Qt
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.last_valid_frame = frame
        return frame

    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
