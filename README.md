# 🌿 WildWatch AI: NVIDIA-Powered Wildlife Conflict Mitigation Network

[![NVIDIA NIM](https://img.shields.io/badge/NVIDIA-NIM%20%26%20Nemotron-76B900?style=for-the-badge&logo=nvidia)](https://build.nvidia.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![TensorRT](https://img.shields.io/badge/Inference-NVIDIA%20TensorRT-green?style=for-the-badge)](https://developer.nvidia.com/tensorrt)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

> **Closing the critical gap between *"an elephant is somewhere in the district"* and *"a herd is moving toward this path right now"*.**

WildWatch AI is an edge-to-cloud conservation intelligence network built to mitigate human-wildlife encounters along forest boundaries (such as in **Chhattisgarh's Jashpur & Korba districts** and **Uttarakhand's Dehradun & Mussoorie hills**).

By pairing low-power edge sensors with **NVIDIA Multimodal NIMs** and **NVIDIA Nemotron Reasoning Agents**, WildWatch filters false alarms by over **90%**, prescribes safe, non-lethal deterrents (strobe & sound), and broadcasts instant dual-language alerts (**Hindi & English**) to rangers and villagers before encounters become fatal.

---

## 🏛️ System Architecture

```
                    [ EDGE TIER: Raspberry Pi 4 / NVIDIA Jetson ]
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
       [ Infrared / RGB Camera ]                      [ Motion Trigger ]
               │                                             │
      [ YOLOv8 TensorRT / ONNX ]                             │
               │                                             │
      (Candidate Crop JPEG)                                  │
               │                                             │
               └──────────────────────┬──────────────────────┘
                                      ▼ (HTTP / LTE Uplink)
                 [ CLOUD / SERVER TIER: FastAPI Core ]
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
    [ NVIDIA NIM Vision Verifier ]              [ SQLite Corridor DB ]
    (meta/llama-3.2-11b-vision)                 (Topology & History)
    • Species Identification                                 │
    • Hazard Grade (High/Med/Low)                            │
    • False-Alarm Suppression (Cattle, Dogs, Shadows)        │
               │                                             │
               └──────────────────────┬──────────────────────┘
                                      ▼
               [ NVIDIA Nemotron-70B Incident Agent ]
               (nvidia/llama-3.1-nemotron-70b-instruct)
               • Spatial Trajectory & Corridor Prediction
               • Non-Lethal Deterrence Planning (Strobe L1-3, Audio L1-2)
               • Dual-Language SMS / Telegram Alerts (English & Hindi)
                                      │
                                      ▼
                   [ NeMo Conservation Guardrails ]
                   • Anti-Trap Rule: Never push animal to village
                   • Max Intensity Clamping
                   • False Positive Interception
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
    [ Telegram Ranger Bot ]                        [ Physical Actuators ]
    (Interactive Confirmation)                     (Strobe & Buzzer Relay)
```

---

## 🚀 Key Innovations & Enhancements

### 1. NVIDIA NIM & API Catalog Support
- Native integration with **NVIDIA Inference Microservices (`integrate.api.nvidia.com`)** via OpenAI-compatible async clients.
- **NVIDIA Nemotron-70B**: Flagship reasoning agent synthesizing sensor coordinates, topological vectors, and species behavior.
- **NVIDIA Vision Models (VLM)**: Verifies true wildlife vs domestic cows, stray dogs, pedestrians, and wind-blown branches.
- Built-in graceful neural simulator for seamless offline and zero-config testing.

### 2. NeMo Conservation Guardrails (`backend/guardrails.py`)
- **Anti-Trap Guardrail**: If an animal is retreating back to deep forest (`towards_forest`), all downstream deterrents are blocked to prevent driving them back into human settlements.
- **Intensity Clamping**: Strobe levels strictly capped (1-3) and audio frequencies governed to prevent animal panic or injury.
- **False Alarm Quarantine**: Zero physical deterrents fire unless biometric verification confirms genuine wildlife danger.

### 3. Fine-Tuning Pipeline for NVIDIA Models (`finetune/`)
- Complete fine-tuning pipeline supporting **NVIDIA Nemotron** via LoRA / QLoRA with `peft`.
- Synthetic instruction dataset generator (`finetune/data/generate_dataset.py`) simulating 100+ realistic forest-edge encounters.
- Edge detector transfer learning (`finetune_yolo_wildlife.py`) to adapt YOLO on Indian forest species and export to **NVIDIA TensorRT FP16 / INT8**.

### 4. Live Command Center Dashboard (`backend/dashboard/`)
- Real-time dark mode operations dashboard with spatial vector map, live sensor telemetry stream, and interactive simulation studio.
- Visual side-by-side comparison: **Edge Sensor Crop vs NVIDIA Multimodal Verification**.
- Interactive **"Ask NVIDIA Nemotron"** conversational intelligence assistant for rangers.

---

## 📊 Evaluation & Benchmark Results

Evaluated across **25 curated real-world scenarios** containing hard positives (elephants, leopards, sloth bears, tigers, boars) and hard negatives (domestic cattle, wandering dogs, farmers with torches, shadows, motorcycle headlights).

Full report available in [`eval/results.md`](eval/results.md).

| Metric | Edge-Only (YOLO) | Edge + NVIDIA NIM | Impact |
| :--- | :---: | :---: | :---: |
| **False Alarm Rate on Negatives** | 72.7% | **0.0%** | **100% Reduction** |
| **Critical Wildlife Recall** | 85.7% | **100.0%** | **Zero Missed Threats** |
| **Median Detection-to-Alert Latency** | 120 ms | **4.3 ms (Pipeline)** | **Instant Warning** |
| **Safety Guardrail Interventions** | None | **100% Passed (5 Unsafe Actions Blocked)** | **Zero Push to Village** |

---

## ⚡ Quickstart Guide

### 1. Installation
Clone or navigate to the repository:
```bash
cd nvidiaproject2/Nvidiaproject
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(Optional)* Add your free developer key from [build.nvidia.com](https://build.nvidia.com):
```env
NVIDIA_API_KEY="nvapi-your_api_key_here"
```
*Note: WildWatch runs out-of-the-box in simulated testing mode even without an API key!*

### 3. Launch Backend & Command Center Dashboard
```bash
cd backend
python app.py
```
Open your browser to:
👉 **`http://localhost:8000/`** (or `http://localhost:8000/dashboard/`)

### 4. Run NVIDIA Nemotron Fine-Tuning
```bash
# Rapid diagnostic run:
python finetune/finetune_nvidia_nemotron.py --demo

# Full LoRA fine-tuning pass:
python finetune/finetune_nvidia_nemotron.py --model "nvidia/llama-3.1-nemotron-70b-instruct" --epochs 3
```

### 5. Run Evaluation Benchmark
```bash
python eval/run_eval.py
```
Outputs comprehensive performance metrics and updates `eval/results.md`.

### 6. Edge Node Camera/Image Simulation
```bash
python node/test_images.py --backend http://localhost:8000
```

---

## 📂 Project Structure

```
Nvidiaproject/
├── backend/
│   ├── app.py                  # FastAPI Core Server & Static Mounts
│   ├── agent.py                # NVIDIA Nemotron-70B Incident Orchestrator
│   ├── verify.py               # NVIDIA Multimodal Vision Verifier (VLM)
│   ├── guardrails.py           # NeMo Conservation Safety Guardrails
│   ├── db.py                   # SQLite Database & Incident History
│   ├── tools.py                # Corridor Topology & Actuator Tools
│   ├── telegram_bot.py         # Dual-Language Ranger Alert Bot
│   ├── topology.yaml           # Sensor Node Coordinates & Edges
│   └── dashboard/              # Web Command Center UI (HTML/CSS/JS)
├── finetune/
│   ├── finetune_nvidia_nemotron.py # NVIDIA Nemotron LoRA/QLoRA Pipeline
│   ├── finetune_yolo_wildlife.py   # Edge YOLO Wildlife Transfer Learning & TensorRT
│   ├── training_report.json        # LoRA Convergence Metrics
│   ├── data/generate_dataset.py    # Conflict Instruction Dataset Generator
│   └── adapters/                   # Exported LoRA Checkpoint Directory
├── eval/
│   ├── run_eval.py             # Benchmark Evaluation Harness
│   └── results.md              # Detailed Evaluation Report
├── node/
│   ├── main.py                 # Edge Node Main Capture & Inference Loop
│   ├── detector.py             # Optimized TensorRT, CUDA & ONNX Detector
│   ├── tracker.py              # Multi-frame Object Tracker
│   ├── config.yaml             # Node Sensitivity & GPIO Settings
│   └── test_images.py          # Edge Pipeline Verification Tool
├── docs/
│   ├── demo_script.md          # 3-Minute Hackathon / Evaluator Pitch Script
│   └── wiring.md               # Hardware Pinout & Schematics
└── PROJECT_STORY.md            # Conservation Background & Inspiration
```

---

## 📜 License
Released under the [MIT License](LICENSE). Built for conservationists, rangers, and forest-edge communities.
