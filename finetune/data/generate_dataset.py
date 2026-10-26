"""
Wildlife Incident Dataset Generator for NVIDIA Nemotron & Llama Fine-Tuning.
Generates instruction-tuning datasets for edge human-wildlife conflict triage,
spatial reasoning, and bilingual forest alerts (English & Hindi).
"""

import json
import os
import random

DATA_DIR = os.path.dirname(__file__)

SCENARIOS = [
    {
        "species": "elephant",
        "node_id": "node-a",
        "direction": "towards_village",
        "approach": "closing",
        "edge_conf": 0.88,
        "location": "North Forest Edge, Jashpur Corridor",
        "time": "23:45",
        "reasoning": "Herd of Asian elephants detected crossing the trench towards paddy fields. Proximity to sleeping farmers creates urgent fatality risk.",
        "hazard": "high",
        "strobe": 3,
        "sound": 2,
        "target_node": "node-b",
        "en_alert": "CRITICAL: Elephant herd advancing toward village path. Level 3 strobe & acoustic deterrent deployed at Node-B. Forest patrol dispatched.",
        "hi_alert": "गंभीर चेतावनी: हाथियों का झुंड गांव की ओर बढ़ रहा है। नोड-बी पर स्ट्रोब लाइट और सायरन चालू कर दिया गया है। कृपया घरों में रहें।"
    },
    {
        "species": "leopard",
        "node_id": "node-b",
        "direction": "along_ridge",
        "approach": "prowling",
        "edge_conf": 0.82,
        "location": "Thano Range, Dehradun Outskirts",
        "time": "18:20",
        "reasoning": "Subadult leopard stalking along footpath near cattle shed at dusk. High encounter risk for pedestrians returning from temple.",
        "hazard": "high",
        "strobe": 2,
        "sound": 2,
        "target_node": "node-b",
        "en_alert": "HIGH HAZARD: Leopard sighted along ridge trail. Perimeter strobe Level 2 activated. Avoid forest route.",
        "hi_alert": "खतरा: पगडंडी के पास तेंदुआ देखा गया है। सुरक्षा लाइट चालू कर दी गई है। जंगल के रास्ते से न जाएं।"
    },
    {
        "species": "sloth_bear",
        "node_id": "node-c",
        "direction": "towards_crops",
        "approach": "foraging",
        "edge_conf": 0.79,
        "location": "Kawardha Forest Edge, Chhattisgarh",
        "time": "04:15",
        "reasoning": "Mother sloth bear with cub foraging in maize border. High aggression potential if startled by early morning workers.",
        "hazard": "high",
        "strobe": 2,
        "sound": 1,
        "target_node": "node-c",
        "en_alert": "WARNING: Sloth bear active in agricultural boundary. Acoustic deterrent active. Warn early morning laborers.",
        "hi_alert": "चेतावनी: खेतों के पास भालू देखा गया है। सुबह काम पर जाने वाले ग्रामीण सतर्क रहें।"
    },
    {
        "species": "wild_boar",
        "node_id": "node-a",
        "direction": "crossing_path",
        "approach": "steady",
        "edge_conf": 0.84,
        "location": "Sector 1 Perimeter",
        "time": "21:10",
        "reasoning": "Sounder of wild boars moving across path. Low threat to human life, but high crop damage potential.",
        "hazard": "medium",
        "strobe": 1,
        "sound": 1,
        "target_node": "node-a",
        "en_alert": "CAUTION: Wild boar group near boundary fence. Low-level acoustic deterrent active to protect crops.",
        "hi_alert": "सूचना: बाड़ के पास जंगली सुअर देखे गए हैं। हल्का सायरन चालू है।"
    },
    {
        "species": "nilgai",
        "node_id": "node-d",
        "direction": "along_highway",
        "approach": "grazing",
        "edge_conf": 0.89,
        "location": "Buffer Zone Highway Strip",
        "time": "16:40",
        "reasoning": "Nilgai herd grazing near road. Highway collision hazard; no immediate village threat.",
        "hazard": "medium",
        "strobe": 1,
        "sound": 0,
        "target_node": "node-d",
        "en_alert": "ADVISORY: Nilgai herd spotted near perimeter road. Slow beacon active to warn motorists.",
        "hi_alert": "सूचना: सड़क के पास नीलगाय का झुंड देखा गया है। वाहन चालक गति धीमी रखें।"
    },
    {
        "species": "cattle",
        "node_id": "node-a",
        "direction": "towards_forest",
        "approach": "wandering",
        "edge_conf": 0.91,
        "location": "Village Grazing Land",
        "time": "17:15",
        "reasoning": "Domestic grazing cows returning to village. Harmless domestic livestock. Suppress alarms.",
        "hazard": "none",
        "strobe": 0,
        "sound": 0,
        "target_node": "none",
        "en_alert": "",
        "hi_alert": ""
    },
    {
        "species": "person",
        "node_id": "node-b",
        "direction": "towards_forest",
        "approach": "walking",
        "edge_conf": 0.94,
        "location": "Village Boundary Trail",
        "time": "06:00",
        "reasoning": "Local farmer walking with torch. Non-wildlife detection. Suppress all deterrents.",
        "hazard": "none",
        "strobe": 0,
        "sound": 0,
        "target_node": "none",
        "en_alert": "",
        "hi_alert": ""
    },
    {
        "species": "shadow_or_foliage",
        "node_id": "node-a",
        "direction": "static",
        "approach": "wind_motion",
        "edge_conf": 0.42,
        "location": "Sensor Canopy",
        "time": "01:22",
        "reasoning": "Wind gust swaying tree branches. False positive motion trigger. Zero action required.",
        "hazard": "none",
        "strobe": 0,
        "sound": 0,
        "target_node": "none",
        "en_alert": "",
        "hi_alert": ""
    }
]

def generate_dataset(output_path=None, num_samples=150):
    if output_path is None:
        output_path = os.path.join(DATA_DIR, "wildlife_nemotron_instructions.jsonl")

    samples = []
    
    for i in range(num_samples):
        base = random.choice(SCENARIOS)
        sample_id = f"WW-FT-{i+1:04d}"
        
        # System Prompt
        system_prompt = (
            "You are the WildWatch Autonomous Wildlife Incident Orchestrator powered by NVIDIA Nemotron.\n"
            "Analyze sensor telemetry, verify wildlife presence, evaluate spatial hazard, and formulate a proportional "
            "non-lethal response and bilingual warning message."
        )

        user_prompt = (
            f"Sensor Node: {base['node_id']}\n"
            f"Location: {base['location']}\n"
            f"Detected Class: {base['species']}\n"
            f"Edge Confidence: {base['edge_conf']:.2f}\n"
            f"Movement Vector: {base['direction']} ({base['approach']})\n"
            f"Time of Sighting: {base['time']}\n\n"
            "Determine the verification verdict, safety actions, and alert message."
        )

        actions = []
        if base["hazard"] != "none":
            if base["strobe"] > 0:
                actions.append({"type": "deterrent", "action": "strobe", "level": base["strobe"], "target": base["target_node"]})
            if base["sound"] > 0:
                actions.append({"type": "deterrent", "action": "sound", "level": base["sound"], "target": base["node_id"]})
            if base["en_alert"]:
                actions.append({"type": "alert", "message": f"{base['en_alert']} / {base['hi_alert']}"})

        response_obj = {
            "incident_id": sample_id,
            "species": base["species"],
            "hazard_level": base["hazard"],
            "is_real_wildlife": base["hazard"] != "none",
            "biologist_reasoning": base["reasoning"],
            "actions": actions
        }

        # Format compatible with NVIDIA NeMo and HuggingFace PEFT / SFT
        sample = {
            "id": sample_id,
            "conversations": [
                {"from": "system", "value": system_prompt},
                {"from": "human", "value": user_prompt},
                {"from": "gpt", "value": json.dumps(response_obj, indent=2, ensure_ascii=False)}
            ]
        }
        samples.append(sample)

    with open(output_path, "w", encoding="utf-8") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")

    print(f"[Dataset Generator] Successfully generated {len(samples)} fine-tuning samples -> {output_path}")
    return output_path

if __name__ == "__main__":
    generate_dataset()
