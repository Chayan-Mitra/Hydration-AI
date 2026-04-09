import cv2
import numpy as np
import time
from ultralytics import YOLO
import mediapipe as mp


class VisionSystem:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")

        self.mp_face = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands

        self.face_mesh = self.mp_face.FaceMesh()
        self.hands = self.mp_hands.Hands()

        self.cap = cv2.VideoCapture(0)

        # detection state
        self.hold_start = None
        self.prev_hand = None
        self.stable_frames = 0
        self.last_sip_time = 0

        # performance
        self.frame_count = 0
        self.yolo_interval = 5
        self.bottle_detected = False

    def start_camera(self):
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)

    def stop_camera(self):
        if self.cap.isOpened():
            self.cap.release()
            cv2.destroyAllWindows()

    def distance(self, a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    def detect_drink(self):
        ret, frame = self.cap.read()
        if not ret:
            return False, None

        self.frame_count += 1
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mouth = None
        hand = None

        # -------- YOLO (every few frames) --------
        if self.frame_count % self.yolo_interval == 0:
            results = self.model(frame, imgsz=320, conf=0.3, verbose=False)
            self.bottle_detected = False

            for r in results:
                for box in r.boxes:
                    cls = int(box.cls[0])
                    label = self.model.names[cls]

                    if label in ["bottle", "cup"]:
                        self.bottle_detected = True
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

        # -------- FACE --------
        face_res = self.face_mesh.process(rgb)
        if face_res.multi_face_landmarks:
            for lm in face_res.multi_face_landmarks:
                mouth_point = lm.landmark[13]
                mouth = (int(mouth_point.x * w), int(mouth_point.y * h))
                cv2.circle(frame, mouth, 5, (0, 255, 0), -1)

        # -------- HAND --------
        hand_res = self.hands.process(rgb)
        if hand_res.multi_hand_landmarks:
            for lm in hand_res.multi_hand_landmarks:
                p = lm.landmark[8]
                hand = (int(p.x * w), int(p.y * h))
                cv2.circle(frame, hand, 5, (255, 0, 0), -1)

        # -------- FINAL DETECTION --------
        if mouth and hand:
            d = self.distance(mouth, hand)

            # relaxed condition: hand near mouth OR bottle detected
            near_mouth = d < 120 or self.bottle_detected
            current_time = time.time()

            # cooldown (prevents double counting)
            if current_time - self.last_sip_time < 2.0:
                return False, frame

            if near_mouth:
                if self.hold_start is None:
                    self.hold_start = current_time
                    self.prev_hand = hand
                    self.stable_frames = 0

                else:
                    move_dist = self.distance(hand, self.prev_hand)

                    if move_dist < 30:
                        self.stable_frames += 1
                    else:
                        self.stable_frames = max(0, self.stable_frames - 1)

                    self.prev_hand = hand
                    hold_time = current_time - self.hold_start

                    # final trigger (balanced for real life)
                    if hold_time > 0.7 and self.stable_frames > 1:
                        print("DRINK DETECTED 💧🔥")

                        self.hold_start = None
                        self.stable_frames = 0
                        self.last_sip_time = current_time

                        return True, frame

            else:
                self.hold_start = None
                self.stable_frames = 0

        return False, frame

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()