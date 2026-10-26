import os
import sys
import time
import base64
import urllib.request
import json
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from detector import ObjectDetector

TEST_IMAGES = {
    "horses": "https://raw.githubusercontent.com/pjreddie/darknet/master/data/horses.jpg",
    "dog": "https://raw.githubusercontent.com/pjreddie/darknet/master/data/dog.jpg",
    "person": "https://raw.githubusercontent.com/pjreddie/darknet/master/data/person.jpg",
    "eagle": "https://raw.githubusercontent.com/pjreddie/darknet/master/data/eagle.jpg"
}

def download_image(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        arr = np.asarray(bytearray(resp.read()), dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="WildWatch Image Pipeline Tester")
    parser.add_argument("--backend", default="http://localhost:8000", help="URL of the WildWatch backend")
    args = parser.parse_args()

    print("=" * 65, flush=True)
    print("      WILDWATCH: CAMERA-FREE IMAGE PIPELINE TESTER", flush=True)
    print("=" * 65, flush=True)
    
    model_path = os.path.join(os.path.dirname(__file__), "models", "yolov8n.onnx")
    detector = ObjectDetector(path=model_path, size=320)

    out_dir = os.path.join(os.path.dirname(__file__), "test_output")
    os.makedirs(out_dir, exist_ok=True)

    backend_url = args.backend.rstrip('/')
    print(f"Cloud Backend target: {backend_url}", flush=True)

    backend_online = False
    try:
        req = urllib.request.Request(f"{backend_url}/health")
        with urllib.request.urlopen(req, timeout=2) as r:
            if r.status == 200:
                backend_online = True
                print(">>> Backend is ONLINE and responding!", flush=True)
    except Exception:
        print(">>> Backend is offline (events will be demonstrated locally).", flush=True)

    print("\nDownloading test images and running detection...\n", flush=True)

    for name, url in TEST_IMAGES.items():
        print("-" * 55, flush=True)
        print(f"Testing Subject: {name.upper()}", flush=True)
        print(f"Downloading from {url}...", flush=True)
        try:
            img = download_image(url)
        except Exception as e:
            print(f"Failed to download {name}: {e}", flush=True)
            continue

        h, w = img.shape[:2]
        print(f"Image Resolution: {w}x{h}. Running neural inference...", flush=True)
        t0 = time.time()
        detections = detector.detect(img)
        dt = (time.time() - t0) * 1000.0

        print(f"Inference Time: {dt:.1f} ms | Found: {len(detections)} object(s)", flush=True)
        annotated = img.copy()

        for i, det in enumerate(detections):
            cls = det["class"]
            conf = det["conf"]
            bbox = det["bbox"]
            x1, y1, x2, y2 = map(int, bbox)

            print(f"  [+] Detected: {cls.upper()} ({conf*100:.1f}%) at [{x1}, {y1}, {x2}, {y2}]", flush=True)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(annotated, f"{cls} {conf:.2f}", (x1, max(y1 - 10, 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            crop = img[max(0, y1):min(h, y2), max(0, x1):min(w, x2)]
            _, buffer = cv2.imencode('.jpg', crop)
            crop_b64 = base64.b64encode(buffer).decode('utf-8')

            event_payload = {
                "node_id": "node-a",
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "track_id": i + 1,
                "edge_class": cls,
                "edge_conf": round(conf, 2),
                "bbox": [float(x) for x in bbox],
                "direction": "approaching",
                "approach": "closing",
                "frames_seen": 4,
                "crop_jpeg_b64": crop_b64,
                "node_health": {"fps": 8.5, "cpu_temp": 45.0, "online": True}
            }

            if backend_online:
                try:
                    data_bytes = json.dumps(event_payload).encode('utf-8')
                    req = urllib.request.Request(
                        f"{backend_url}/events",
                        data=data_bytes,
                        headers={"Content-Type": "application/json"}
                    )
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        res_json = json.loads(resp.read().decode('utf-8'))
                        print(f"      >>> [Uplink Sent] Cloud accepted event! ID: {res_json.get('event_id')}", flush=True)
                except Exception as ex:
                    print(f"      >>> [Uplink Error]: {ex}", flush=True)

        out_path = os.path.join(out_dir, f"detected_{name}.jpg")
        cv2.imwrite(out_path, annotated)
        print(f"Saved annotated image: {out_path}", flush=True)

    print("\n" + "=" * 65, flush=True)
    print("ALL TESTS COMPLETE! Check 'test_output/' for saved images.", flush=True)
    print("=" * 65, flush=True)

if __name__ == "__main__":
    main()
