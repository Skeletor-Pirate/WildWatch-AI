# WildWatch AI: 3-Minute Live Demo & Pitch Script

This script walks through presenting WildWatch AI to judges, forest officials, or technical evaluators.

---

## 1. The Hook (0:00 - 0:45)
- **The Problem**: In forest-edge villages across Chhattisgarh (Jashpur, Korba) and Uttarakhand (Dehradun, Mussoorie), human-wildlife encounters claim hundreds of lives every year.
- **The Gap**: Existing warning systems fail in two ways:
  1. Warnings arrive too late (when the animal has already reached the hut or path).
  2. Edge sensors trigger so many false alarms (cows, stray dogs, swaying branches) that villagers turn them off.
- **The Solution**: **WildWatch AI** — a distributed edge-to-cloud conservation network pairing low-power edge triggers with **NVIDIA Multimodal AI & Nemotron Reasoning**.

---

## 2. Live Architecture Walkthrough (0:45 - 1:45)
1. **Launch the Command Center**:
   ```bash
   cd c:\Users\HP\app\nvidiaproject2\Nvidiaproject\backend
   python app.py
   ```
   Open browser at: `http://localhost:8000/`

2. **Demonstrate False Alarm Suppression**:
   - In the **Simulation Studio**, click **`🐄 Grazing Cow (Filter Test)`** or **`👤 Villager Torch (False Alarm)`**.
   - Show how the edge sensor triggered on movement, but **NVIDIA Vision Model** recognized domestic livestock, and **NeMo Guardrails** immediately suppressed the alarms.
   - Result: Zero alarm fatigue for villagers.

3. **Demonstrate Critical Incident Response**:
   - Click **`🐘 Elephant Herd (High Hazard)`**.
   - Watch the live spatial threat vector illuminate along the trail.
   - Point to the **NVIDIA Vision Verifier**: verified Asian Elephant, High Hazard.
   - Point to the **NVIDIA Nemotron Plan**:
     - Automatically actuated **Strobe Level 3** ahead of the herd at Node-B.
     - Armed **Acoustic Level 2** deterrent to divert them back to the forest.
     - Dispatched a dual-language **Telegram warning** in English & Hindi for local forest guards and villagers.

---

## 3. Fine-Tuning & NVIDIA Ecosystem (1:45 - 2:30)
Showcase how we fine-tune NVIDIA foundational models for this domain:
```bash
python finetune/finetune_nvidia_nemotron.py --demo
```
- Highlight:
  - Generates specialized Indian forest conflict instruction sets.
  - Fine-tunes **NVIDIA Nemotron** via LoRA / QLoRA adapters for spatial reasoning and non-lethal rules.
  - Exports lightweight adapters and converts edge YOLO models to **NVIDIA TensorRT** for high-FPS edge acceleration.

---

## 4. Closing & Evaluation Numbers (2:30 - 3:00)
- **Evaluation Proof (`eval/results.md`)**:
  - **100% False Alarm Reduction** on hard negatives (cattle, shadows, farmers).
  - **100% True Wildlife Recall** across elephants, leopards, sloth bears, tigers, and boars.
  - **4.3 ms Median Pipeline Latency**.
  - **100% Guardrail Compliance**: zero push toward human settlements.
- **Final Word**: WildWatch turns wildlife conflict from a fatal tragedy into a predictable, manageable, non-lethal encounter.
