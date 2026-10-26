import time
import cv2
import base64

class TriggerLogic:
    def __init__(self, thresholds, trigger_cfg):
        self.thresholds = thresholds
        self.min_frames = trigger_cfg.get("min_frames", 3)
        self.cooldown = trigger_cfg.get("cooldown", 5)
        self.track_frames = {}
        self.last_trigger = {}

    def process(self, tracks, frame):
        events = []
        now = time.time()
        for track in tracks:
            cls = track['class']
            conf = track['conf']
            tid = track['id']
            
            thresh = self.thresholds.get(cls, self.thresholds.get("default", 0.5))
            if conf >= thresh:
                self.track_frames[tid] = self.track_frames.get(tid, 0) + 1
            else:
                self.track_frames[tid] = 0
                
            if self.track_frames[tid] >= self.min_frames:
                last_t = self.last_trigger.get(tid, 0)
                if now - last_t > self.cooldown:
                    self.last_trigger[tid] = now
                    
                    x1, y1, x2, y2 = map(int, track['bbox'])
                    crop = frame[max(0, y1):min(frame.shape[0], y2), max(0, x1):min(frame.shape[1], x2)]
                    _, buffer = cv2.imencode('.jpg', crop)
                    crop_b64 = base64.b64encode(buffer).decode('utf-8')
                    
                    event = {
                        "track_id": tid,
                        "edge_class": cls,
                        "edge_conf": float(conf),
                        "bbox": [float(c) for c in track['bbox']],
                        "direction": track.get("direction", "unknown"),
                        "approach": "closing",
                        "frames_seen": self.track_frames.get(tid, 1),
                        "crop_jpeg_b64": crop_b64,
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))
                    }
                    events.append(event)
        return events