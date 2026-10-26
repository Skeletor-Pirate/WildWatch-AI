# WildWatch Fine-Tuning Suite for NVIDIA Models

This directory provides complete, end-to-end fine-tuning workflows to adapt NVIDIA foundational models and edge vision detectors specifically for human-wildlife conflict prevention in forest-edge communities.

---

## 1. NVIDIA Nemotron LoRA Fine-Tuning (`finetune_nvidia_nemotron.py`)

Fine-tunes **NVIDIA Nemotron** (`nvidia/llama-3.1-nemotron-70b-instruct` or `nvidia/nemotron-mini-4b-instruct`) using Low-Rank Adaptation (LoRA / QLoRA) on specialized conflict triage telemetry.

### What it teaches the model:
- **Spatial Reasoning**: Tracking animal movement vectors (`towards_village`, `along_ridge`, `towards_forest`) and predicting downstream corridor impact.
- **Safety Guardrails**: Zero lethal force; strictly non-lethal acoustic chirps and safe light strobes.
- **Bilingual Alerts**: Automatic generation of simultaneous Hindi and English broadcast messages for local forest guards, villagers, and panchayat admins.
- **False Alarm Suppression**: Distinguishing between wild apex predators/elephants vs grazing cows, stray dogs, and local villagers.

### How to Run:
```bash
# 1. Generate instruction dataset (100+ conflict scenarios)
python finetune/data/generate_dataset.py

# 2. Run LoRA Fine-Tuning pass
python finetune/finetune_nvidia_nemotron.py --model "nvidia/llama-3.1-nemotron-70b-instruct" --epochs 3

# For a quick demonstration run:
python finetune/finetune_nvidia_nemotron.py --demo
```

### Outputs:
- LoRA Adapters saved in `finetune/adapters/nemotron_wildwatch_lora/`
- Training metrics and loss convergence report in `finetune/training_report.json`

---

## 2. Edge Wildlife YOLO Transfer Learning & TensorRT (`finetune_yolo_wildlife.py`)

Standard COCO models lack critical Indian wildlife species (e.g. Leopard, Sloth Bear, Nilgai, Wild Boar). This script adapts YOLOv8 on custom forest classes and exports the weights directly to an **NVIDIA TensorRT FP16 / INT8** engine for ultra-low latency inference on NVIDIA Jetson or RTX GPUs.

### How to Run:
```bash
python finetune/finetune_yolo_wildlife.py --epochs 5 --imgsz 320
```

---

## Hardware Compatibility
- **NVIDIA RTX 40-Series / RTX 30-Series / A100 / H100**: Direct CUDA and TensorRT acceleration.
- **NVIDIA Jetson (Orin Nano, Orin NX, Xavier)**: High-efficiency edge inference (< 15ms latency).
- **CPU / ARM (Raspberry Pi 4)**: Fallback ONNX Runtime execution provider.
