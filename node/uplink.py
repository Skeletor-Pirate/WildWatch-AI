import requests
import time
import logging

logger = logging.getLogger("Uplink")

class UplinkClient:
    def __init__(self, url, node_id):
        self.url = url
        self.node_id = node_id
        self.online = False

    def is_online(self):
        try:
            resp = requests.get(f"{self.url}/health", timeout=2)
            self.online = resp.status_code == 200
        except:
            self.online = False
        return self.online

    def send_event(self, event):
        payload = {
            "node_id": self.node_id,
            **event
        }
        retries = 3
        backoff = 1
        for i in range(retries):
            try:
                resp = requests.post(f"{self.url}/api/events", json=payload, timeout=5)
                if resp.status_code == 200:
                    return True
            except requests.exceptions.RequestException as e:
                logger.error(f"Uplink error: {e}")
            time.sleep(backoff)
            backoff *= 2
        return False