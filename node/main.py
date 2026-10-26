import argparse
import time
import cv2
import yaml
import logging

from capture import VideoCapture
from detector import ObjectDetector
from tracker import ObjectTracker
from trigger import TriggerLogic
from uplink import UplinkClient
from offline_queue import OfflineQueue
from actuators import ActuatorController
from fallback import FallbackLogic
from health import HealthMonitor
from cmd_listener import CommandListener
from direction import DirectionEstimator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NodeMain")

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="WildWatch Edge Node")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--video", default=None, help="Path to video file or RTSP/HTTP camera stream URL")
    args = parser.parse_args()

    config = load_config(args.config)
    node_id = config.get("node_id", "unknown-node")
    
    logger.info(f"Starting WildWatch Node: {node_id}")

    # Initialize components
    video_source = args.video or config.get("camera", {}).get("source", "auto")
    cap = VideoCapture(source=video_source)
    detector = ObjectDetector(config.get("model_path", "model.pt"), config.get("model_size", (640,640)))
    tracker = ObjectTracker()
    direction_est = DirectionEstimator()
    trigger = TriggerLogic(config.get("thresholds", {}), config.get("trigger", {}))
    queue = OfflineQueue("events_queue.db")
    
    backend_url = config.get("backend", {}).get("url", "http://localhost:5000")
    health_interval = config.get("backend", {}).get("health_interval", 10)
    poll_interval = config.get("backend", {}).get("poll_interval", 5)
    
    uplink = UplinkClient(backend_url, node_id)
    actuators = ActuatorController(config.get("gpio", {}))
    fallback = FallbackLogic(actuators)
    health = HealthMonitor(uplink, health_interval)
    cmd_listener = CommandListener(uplink, actuators, poll_interval)

    cap.start()
    health.start()
    cmd_listener.start()

    try:
        while True:
            frame = cap.read()
            if frame is None:
                time.sleep(0.1)
                continue

            health.tick_frame()

            # Detect
            detections = detector.detect(frame)
            
            # Track
            tracks = tracker.update(detections)
            
            for t in tracks:
                t['direction'] = direction_est.analyze(t)
            
            # Trigger Logic
            events = trigger.process(tracks, frame)
            
            for event in events:
                if uplink.is_online():
                    # Send queue first
                    if not queue.is_empty():
                        for q_item in queue.get_all():
                            success = uplink.send_event(q_item["event"])
                            if success:
                                queue.remove(q_item["db_id"])
                    
                    # Send current event
                    success = uplink.send_event(event)
                    if not success:
                        queue.add(event)
                else:
                    queue.add(event)
                    fallback.handle_offline_event(event)

            # Target loop delay to maintain target FPS
            time.sleep(1.0 / config.get("target_fps", 5))

    except KeyboardInterrupt:
        logger.info("Shutting down node...")
    finally:
        cap.stop()
        health.stop()
        cmd_listener.stop()
        actuators.cleanup()

if __name__ == "__main__":
    main()
