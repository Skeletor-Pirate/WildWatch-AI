import threading
import time
import requests

class CommandListener:
    def __init__(self, uplink, actuators, interval):
        self.uplink = uplink
        self.actuators = actuators
        self.interval = interval
        self.running = False

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
            if self.uplink.is_online():
                try:
                    resp = requests.get(f"{self.uplink.url}/api/commands?node_id={self.uplink.node_id}", timeout=2)
                    if resp.status_code == 200:
                        cmds = resp.json().get("commands", [])
                        for cmd in cmds:
                            self.actuators.trigger(cmd.get("action"))
                except:
                    pass