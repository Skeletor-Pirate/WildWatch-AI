import os

NODE_DIR = r"c:\Users\harsh\OneDrive\Desktop\Nvidiaproject\node"
BACKEND_DIR = r"c:\Users\harsh\OneDrive\Desktop\Nvidiaproject\backend"

node_files = {
    "capture.py": """
import cv2

class VideoCapture:
    def __init__(self, width=640, height=480):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
    def start(self):
        pass # cap already opened
        
    def read(self):
        ret, frame = self.cap.read()
        return frame if ret else None
        
    def stop(self):
        self.cap.release()
""",
    "detector.py": """
class ObjectDetector:
    def __init__(self, model_path, model_size):
        self.model_path = model_path
        self.model_size = model_size
        
    def detect(self, frame):
        # Mock detection
        return []
""",
    "tracker.py": """
class ObjectTracker:
    def __init__(self):
        self.next_id = 1
        self.objects = {}
        
    def update(self, detections):
        # Mock tracking
        return []
""",
    "trigger.py": """
class TriggerLogic:
    def __init__(self, thresholds, config):
        self.thresholds = thresholds
        self.config = config
        
    def process(self, tracks, frame):
        # Mock trigger
        return []
""",
    "uplink.py": """
import requests

class UplinkClient:
    def __init__(self, backend_url, node_id):
        self.backend_url = backend_url
        self.node_id = node_id
        
    def is_online(self):
        return True
        
    def send_event(self, event):
        return True
""",
    "queue.py": """
class OfflineQueue:
    def __init__(self, db_path):
        self.db_path = db_path
        self.events = []
        
    def is_empty(self):
        return len(self.events) == 0
        
    def get_all(self):
        return self.events
        
    def clear(self):
        self.events = []
        
    def add(self, event):
        self.events.append(event)
""",
    "actuators.py": """
class ActuatorController:
    def __init__(self, gpio_config):
        self.gpio_config = gpio_config
        
    def cleanup(self):
        pass
""",
    "fallback.py": """
class FallbackLogic:
    def __init__(self, actuators):
        self.actuators = actuators
        
    def handle_offline_event(self, event):
        pass
""",
    "health.py": """
import threading
import time

class HealthMonitor:
    def __init__(self, uplink, interval):
        self.uplink = uplink
        self.interval = interval
        self.running = False
        self.thread = None
        
    def _run(self):
        while self.running:
            time.sleep(self.interval)
            
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
""",
    "cmd_listener.py": """
import threading
import time

class CommandListener:
    def __init__(self, uplink, actuators, interval):
        self.uplink = uplink
        self.actuators = actuators
        self.interval = interval
        self.running = False
        self.thread = None
        
    def _run(self):
        while self.running:
            time.sleep(self.interval)
            
    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
"""
}

backend_files = {
    "db.py": """
import sqlite3

DB_PATH = 'wildwatch.db'

def init_db():
    pass

def store_event(event_id, event_dict):
    pass

def store_verification(event_id, result_dict):
    pass

def queue_command(node_id, action):
    pass

def get_queued_commands(node_id):
    return []
""",
    "verify.py": """
async def verify_event(event_data):
    return {"is_real_animal": True, "confidence": 0.9}
""",
    "agent.py": """
async def process_verified_event(event_id, event_data, verification_result):
    return [{"type": "deterrent", "action": "strobe", "level": 1}]
""",
    "guardrails.py": """
def check_actions(actions, event_data):
    return actions
"""
}

def write_files(directory, file_map):
    for filename, content in file_map.items():
        with open(os.path.join(directory, filename), 'w') as f:
            f.write(content.strip())

write_files(NODE_DIR, node_files)
write_files(BACKEND_DIR, backend_files)

print("Files rewritten successfully.")
