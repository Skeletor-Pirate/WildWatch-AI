import os
import cv2
import numpy as np
import logging

logger = logging.getLogger("EdgeDetector")

COCO_CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
    'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
    'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
    'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
    'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
    'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
    'hair drier', 'toothbrush'
]

# Extended Wildlife Classes for fine-tuned models
WILDLIFE_CLASSES = [
    'elephant', 'leopard', 'tiger', 'sloth_bear', 'wild_boar', 'nilgai', 'deer',
    'monkey', 'langur', 'cow', 'person', 'dog', 'vehicle'
]

class ObjectDetector:
    """
    Optimized Edge Object Detector with NVIDIA TensorRT & CUDA GPU acceleration,
    ONNX Runtime, and OpenCV DNN / Ultralytics fallbacks.
    """
    def __init__(self, path="models/yolov8n.onnx", size=320):
        self.path = path
        self.imgsz = int(size[0]) if isinstance(size, (list, tuple)) else int(size)
        self.mode = None
        self.session = None
        self.net = None
        self.model = None
        self.device = "cpu"

        candidate_paths = [
            path,
            os.path.join(os.path.dirname(__file__), "models", "yolov8n.onnx"),
            os.path.join(os.path.dirname(__file__), "..", "yolov8n.onnx"),
            "models/yolov8n.onnx",
            "yolov8n.onnx"
        ]
        onnx_file = next((p for p in candidate_paths if p and os.path.exists(p)), None)

        # 1. Check for NVIDIA TensorRT / CUDA with ONNX Runtime
        if onnx_file:
            try:
                import onnxruntime as ort
                available_providers = ort.get_available_providers()
                logger.info(f"[Detector] Available ONNX providers: {available_providers}")

                providers = []
                if 'TensorrtExecutionProvider' in available_providers:
                    providers.append('TensorrtExecutionProvider')
                    self.device = "tensorrt"
                if 'CUDAExecutionProvider' in available_providers:
                    providers.append('CUDAExecutionProvider')
                    self.device = "cuda"
                providers.append('CPUExecutionProvider')

                opts = ort.SessionOptions()
                # On Pi or single core, limit threads; on GPU, let provider optimize
                if self.device == "cpu":
                    opts.intra_op_num_threads = 2
                    opts.inter_op_num_threads = 1
                opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

                self.session = ort.InferenceSession(onnx_file, opts, providers=providers)
                self.input_name = self.session.get_inputs()[0].name
                self.mode = "onnxruntime"
                logger.info(f"[Detector] ONNX Runtime initialized with [{self.session.get_providers()[0]}] (Device: {self.device})")
                return
            except Exception as e:
                logger.debug(f"[Detector] ONNX Runtime init skipped: {e}")

        # 2. Try OpenCV DNN (with CUDA backend if compiled with CUDA)
        if onnx_file:
            try:
                self.net = cv2.dnn.readNetFromONNX(onnx_file)
                # Check for OpenCV CUDA backend
                try:
                    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                        self.device = "cuda"
                    else:
                        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                except Exception:
                    self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                    self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

                self.mode = "opencv_dnn"
                logger.info(f"[Detector] OpenCV DNN active (Device: {self.device})")
                return
            except Exception as e:
                logger.debug(f"[Detector] OpenCV DNN failed: {e}")

        # 3. Fallback to Ultralytics PyTorch with NVIDIA CUDA FP16 support
        try:
            from ultralytics import YOLO
            import torch

            pt_candidates = [
                path if path.endswith(".pt") else None,
                os.path.join(os.path.dirname(__file__), "yolov8n.pt"),
                os.path.join(os.path.dirname(__file__), "..", "yolov8n.pt"),
                "yolov8n.pt"
            ]
            pt_target = next((p for p in pt_candidates if p and os.path.exists(p)), "yolov8n.pt")

            self.model = YOLO(pt_target)
            if torch.cuda.is_available():
                self.device = "cuda"
                logger.info(f"[Detector] Ultralytics active on NVIDIA GPU: {torch.cuda.get_device_name(0)}")
            else:
                self.device = "cpu"
                logger.info("[Detector] Ultralytics active on CPU")

            self.mode = "ultralytics"
        except Exception as e:
            logger.warning(f"[Detector] No deep learning engine available: {e}")

    def detect(self, frame):
        if frame is None:
            return []

        if self.mode == "onnxruntime":
            return self._detect_onnxruntime(frame)
        elif self.mode == "opencv_dnn":
            return self._detect_opencv_dnn(frame)
        elif self.mode == "ultralytics":
            return self._detect_ultralytics(frame)
        else:
            return []

    def _detect_onnxruntime(self, frame):
        h, w = frame.shape[:2]
        img_resized = cv2.resize(frame, (self.imgsz, self.imgsz))
        img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)
        input_tensor = np.transpose(img_rgb, (2, 0, 1)).astype(np.float32) / 255.0
        input_tensor = np.expand_dims(input_tensor, axis=0)

        outputs = self.session.run(None, {self.input_name: input_tensor})
        predictions = outputs[0][0].T
        return self._postprocess(predictions, w, h)

    def _detect_opencv_dnn(self, frame):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1.0 / 255.0, (self.imgsz, self.imgsz), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward()
        predictions = outputs[0].T
        return self._postprocess(predictions, w, h)

    def _postprocess(self, predictions, w, h):
        boxes, confidences, class_ids = [], [], []
        x_factor = w / float(self.imgsz)
        y_factor = h / float(self.imgsz)

        for row in predictions:
            scores = row[4:]
            max_idx = int(np.argmax(scores))
            max_score = float(scores[max_idx])
            if max_score >= 0.25:
                cx, cy, bw, bh = row[0], row[1], row[2], row[3]
                x1 = int((cx - 0.5 * bw) * x_factor)
                y1 = int((cy - 0.5 * bh) * y_factor)
                boxes.append([x1, y1, int(bw * x_factor), int(bh * y_factor)])
                confidences.append(max_score)
                class_ids.append(max_idx)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.25, 0.45)
        detections = []
        if len(indices) > 0:
            for idx in indices.flatten():
                x1, y1, width, height = boxes[idx]
                cls_id = class_ids[idx]
                cls_name = COCO_CLASSES[cls_id] if cls_id < len(COCO_CLASSES) else f"class_{cls_id}"
                detections.append({
                    "bbox": [float(x1), float(y1), float(x1 + width), float(y1 + height)],
                    "class": cls_name,
                    "conf": float(confidences[idx])
                })
        return detections

    def _detect_ultralytics(self, frame):
        half_precision = (self.device == "cuda")
        results = self.model(frame, imgsz=self.imgsz, device=self.device, half=half_precision, verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                name = self.model.names[cls]
                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "class": name,
                    "conf": conf
                })
        return detections
