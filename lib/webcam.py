import cv2
import time
import threading
import queue
import numpy as np
from collections import deque

class Webcam:
    def __init__(self, model_path, window_width, window_height, rect_color = (255, 0, 0), rect_thickness = 2, rect_padding = 8, fps = 15, pygame = None, video_input = 0):
        self.model_path = model_path
        self.window_width = window_width
        self.window_height = window_height
        self.video_input = video_input
        self.rect_color = rect_color
        self.rect_thickness = rect_thickness
        self.rect_padding = rect_padding
        self.webcam = None
        self.pygame = pygame
        self.fps = fps
        self.frame_interval = 1.0 / fps
        self.last_frame_time = 0
        self.last_frame = None
        self.face_cascade = None
        self.frame_queue = queue.Queue(maxsize = 2)
        self.processed_frame = None
        self.detection_thread = None
        self.running = False
        self._load_cascade()
        self.face_centroid = { "center_x": 0, "center_y": 0 }
        self.has_valid_face = False
        self.webcam_height = 480
        self.webcam_width = 640
        self.face_history = deque(maxlen = 5)
        self.smoothed_face = None

    def _load_cascade(self):
        try:
            self.face_cascade = cv2.CascadeClassifier(self.model_path)
            print("Face cascade loaded successfully")
        except Exception as e:
            print(f"Failed to load face cascade: {e}")
            self.face_cascade = None

    def get_centroid(self):
        return (self.face_centroid["center_x"], self.face_centroid["center_y"])

    def _detection_worker(self):
        while self.running:
            try:
                frame = self.frame_queue.get(timeout = 1.0)
                
                if frame is None:
                    break
                
                processed_frame = self._detect_face(frame)
                self.processed_frame = processed_frame
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Detection worker error: {e}")
                continue

    def _detect_face(self, frame):
        if self.face_cascade is None:
            return frame
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor = 1.1,
                minNeighbors = 5,
                minSize = (32, 32),
                maxSize = (320, 320),
                flags = cv2.CASCADE_SCALE_IMAGE
            )

            if len(faces) > 0:
                faces = sorted(faces, key = lambda rect: rect[2] * rect[3], reverse = True)
                x, y, w, h = faces[0]
                current_face = np.array([x, y, w, h])
                self.face_history.append(current_face)
                smoothed_face = np.mean(self.face_history, axis = 0).astype(int)
                x_smooth, y_smooth, w_smooth, h_smooth = smoothed_face
                center_x = x_smooth + (w_smooth // 2)
                center_y = y_smooth + (h_smooth // 2)
                self.face_centroid = { "center_x": int(center_x), "center_y": int(center_y) }
                x1 = max(0, x_smooth - self.rect_padding)
                y1 = max(0, y_smooth - self.rect_padding)
                x2 = min(frame.shape[1], x_smooth + w_smooth + self.rect_padding)
                y2 = min(frame.shape[0], y_smooth + h_smooth + self.rect_padding)
                cv2.rectangle(frame, (x1, y1), (x2, y2), self.rect_color, self.rect_thickness)
            
            return frame
        except Exception as e:
            print(f"Face detection error: {e}")
            return frame

    def _start_detection_thread(self):
        if self.face_cascade is None:
            return
        
        self.running = True
        self.detection_thread = threading.Thread(target = self._detection_worker)
        self.detection_thread.daemon = True
        self.detection_thread.start()

    def _stop_detection_thread(self):
        self.running = False

        if self.detection_thread and self.detection_thread.is_alive():
            self.frame_queue.put(None)
            self.detection_thread.join(timeout = 1.0)

    def init(self):
        try:
            self.webcam = cv2.VideoCapture(self.video_input)

            if not self.webcam.isOpened():
                print("Webcam not detected")
                return False
            
            self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH, self.webcam_width)
            self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.webcam_height)
            ret, frame = self.webcam.read()

            if not ret:
                print("Webcam not detected, using default background")
                return False
            
            self._start_detection_thread()
            return True
        except Exception as e:
            print(f"Webcam initialization error: {e}")
            return False
        
    def get_background(self):
        if self.webcam is None:
            return None
        
        current_time = time.time()
        elapsed_time = current_time - self.last_frame_time

        if elapsed_time < self.frame_interval and self.last_frame is not None:
            return self.last_frame
        
        ret, frame = self.webcam.read()

        if not ret:
            return self.last_frame
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        if self.running and self.face_cascade is not None:
            try:
                self.frame_queue.put(frame_rgb.copy(), block = False)
            except queue.Full:
                pass
            
            if self.processed_frame is not None:
                frame_rgb = self.processed_frame
        
        original_height, original_width = frame_rgb.shape[:2]
        original_aspect = original_width / original_height
        target_aspect = self.window_height / self.window_width
        
        if original_aspect > (1.0 / target_aspect):
            crop_width = int(original_height * (1.0 / target_aspect))
            start_x = (original_width - crop_width) // 2
            cropped_frame = frame_rgb[:, start_x:start_x + crop_width]
        else:
            crop_height = int(original_width * target_aspect)
            start_y = (original_height - crop_height) // 2
            cropped_frame = frame_rgb[start_y:start_y + crop_height, :]
        
        rotated_frame = cv2.rotate(cropped_frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        resized_frame = cv2.resize(rotated_frame, (self.window_height, self.window_width))
        background = self.pygame.surfarray.make_surface(resized_frame)
        self.last_frame = background
        self.last_frame_time = current_time
        
        return background
    
    def destroy_all(self):
        self._stop_detection_thread()
        
        if self.webcam is not None:
            self.webcam.release()

        cv2.destroyAllWindows()