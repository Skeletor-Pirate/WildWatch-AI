import threading
import time
import requests
import psutil

class HealthMonitor:
    def __init__(self, uplink, interval):
        self.uplink = uplink
        self.interval = interval
        self.running = False
        self.frames = 0
        self.last_time = time.time()

    def tick_frame(self):
        self.frames += 1

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()

    def _run(self):
        while self.running:
            time.sleep(self.interval)
            now = time.time()
            fps = self.frames / (max(now - self.last_time, 0.001))
            self.frames = 0
            self.last_time = now
            
            try:
                temp = psutil.sensors_temperatures().get('coretemp', [])[0].current
            except:
                temp = 0.0
                
            status = {
                "node_id": self.uplink.node_id,
                "fps": round(fps, 2),
                "cpu_temp": temp,
                "cpu_percent": psutil.cpu_percent()
            }
            
            if self.uplink.is_online():
                try:
                    requests.post(f"{self.uplink.url}/api/health", json=status, timeout=2)
                except:
                    pass