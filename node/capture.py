import cv2
import threading
import logging
import numpy as np
import time

logger = logging.getLogger("Capture")

class VideoCapture:
    def __init__(self, source="auto", width=640, height=480):
        self.source = source
        self.width = width
        self.height = height
        self.running = False
        self.frame = None
        self.lock = threading.Lock()
        self.use_picam = False
        self.cap = None
        self.is_synthetic = False

        # 1. If a video file, network stream, or device index is explicitly passed
        if self.source != "auto":
            try:
                # Try integer device index first
                src = int(self.source)
            except ValueError:
                src = self.source
            
            print(f"[Capture] Opening video source: {src}")
            self.cap = cv2.VideoCapture(src)
            if not self.cap.isOpened():
                print(f"[Capture] Failed to open video source: {src}. Falling back to synthetic test feed.")
                self.is_synthetic = True
            return

        # 2. "auto" mode: Try Raspberry Pi CSI Camera
        try:
            from picamera2 import Picamera2
            self.picam2 = Picamera2()
            self.picam2.configure(self.picam2.create_video_configuration(main={"size": (self.width, self.height)}))
            self.use_picam = True
            print("[Capture] Initialized Raspberry Pi Camera (CSI) via Picamera2.")
            return
        except Exception:
            self.use_picam = False

        # 3. "auto" mode: Try connected USB webcams
        for cam_idx in [0, 1, 2]:
            cap_test = cv2.VideoCapture(cam_idx)
            if cap_test.isOpened():
                self.cap = cap_test
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                print(f"[Capture] Successfully opened USB camera on /dev/video{cam_idx}")
                return
            cap_test.release()

        # 4. If test_video.mp4 exists in directory, automatically loop it
        import os
        sample_videos = ["test_video.mp4", "demo.mp4", "sample.mp4"]
        for v in sample_videos:
            if os.path.exists(v):
                print(f"[Capture] No physical camera found. Automatically playing test video: {v}")
                self.cap = cv2.VideoCapture(v)
                return

        # 5. Fallback: Synthetic simulation test pattern
        print("[Capture] No physical camera or video file detected.")
        print("[Capture] Generating SYNTHETIC TEST FEED (virtual simulated camera) so pipeline runs!")
        self.is_synthetic = True

    def start(self):
        self.running = True
        if self.use_picam:
            self.picam2.start()
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _generate_synthetic_frame(self, t):
        # Generates a moving test canvas with timestamp and simulated object motion
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # Background gradient
        frame[:, :] = (30, 35, 40)
        
        # Draw grid
        for x in range(0, self.width, 80):
            cv2.line(frame, (x, 0), (x, self.height), (45, 50, 55), 1)
        for y in range(0, self.height, 60):
            cv2.line(frame, (0, y), (self.width, y), (45, 50, 55), 1)

        # Draw simulated target moving across boundary
        cx = int((np.sin(t * 1.5) * 0.4 + 0.5) * self.width)
        cy = int((np.cos(t * 1.0) * 0.2 + 0.5) * self.height)
        cv2.circle(frame, (cx, cy), 35, (0, 200, 255), -1)
        cv2.putText(frame, "SIMULATED TARGET", (cx - 70, cy - 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)

        # Status overlay
        cv2.putText(frame, "WILDWATCH VIRTUAL CAMERA", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Time: {time.strftime('%H:%M:%S')}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        cv2.putText(frame, "Tip: Plug in a webcam or pass --video <file>", (20, self.height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 150, 180), 1)
        return frame

    def _update(self):
        start_time = time.time()
        while self.running:
            if self.is_synthetic:
                frame = self._generate_synthetic_frame(time.time() - start_time)
                time.sleep(0.05)  # ~20 FPS synthetic loop
            elif self.use_picam:
                try:
                    frame = self.picam2.capture_array()
                except Exception:
                    time.sleep(0.05)
                    continue
            else:
                ret, frame = self.cap.read()
                if not ret:
                    # If reading a video file, loop back to the beginning!
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.cap.read()
                    if not ret:
                        time.sleep(0.05)
                        continue
                time.sleep(0.03)

            frame = cv2.resize(frame, (self.width, self.height))
            with self.lock:
                self.frame = frame

    def read(self):
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()
        return None

    def stop(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()
        if self.use_picam:
            try:
                self.picam2.stop()
                self.picam2.close()
            except Exception:
                pass
        elif self.cap:
            self.cap.release()
