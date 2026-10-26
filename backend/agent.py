import os
import json
import logging
from openai import AsyncOpenAI
from dotenv import load_dotenv

import tools

load_dotenv()
logger = logging.getLogger("NemotronAgent")

# Model & Provider configs
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_LLM_MODEL = os.getenv("NVIDIA_LLM_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")

NEBIUS_API_KEY = os.getenv("NEBIUS_API_KEY", "")
NEBIUS_BASE_URL = os.getenv("NEBIUS_BASE_URL", "https://api.studio.nebius.ai/v1/")
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "meta-llama/Llama-3.1-70B-Instruct")

def get_llm_client():
    """
    Returns an async OpenAI-compatible client for NVIDIA Nemotron NIM or Nebius Token Factory.
    """
    if NVIDIA_API_KEY and (NVIDIA_API_KEY.startswith("nvapi-") or len(NVIDIA_API_KEY) > 10):
        logger.info(f"[NemotronAgent] Connecting to NVIDIA NIM API Catalog ({NVIDIA_LLM_MODEL})...")
        return AsyncOpenAI(base_url=NVIDIA_BASE_URL, api_key=NVIDIA_API_KEY), NVIDIA_LLM_MODEL, "nvidia"

    if NEBIUS_API_KEY and NEBIUS_API_KEY != "your_nebius_api_key_here":
        logger.info(f"[NemotronAgent] Connecting to Nebius Token Factory ({LLM_MODEL_ID})...")
        return AsyncOpenAI(base_url=NEBIUS_BASE_URL, api_key=NEBIUS_API_KEY), LLM_MODEL_ID, "nebius"

    return None, None, "simulation"

async def process_verified_event(event_id: str, event_data: dict, verification_result: dict) -> list:
    """
    Autonomous Incident Orchestrator powered by NVIDIA Nemotron (70B/340B).
    Synthesizes sensor node coordinates, topological vector, animal trajectory, and species biology
    to generate safe, proportional physical deterrent actions and bilingual alerts (English + Hindi).
    """
    node_id = event_data.get("node_id", "unknown-node")
    species = verification_result.get("species", "unknown")
    conf = verification_result.get("confidence", 0.0)
    hazard_level = verification_result.get("hazard_level", "low")
    vlm_reason = verification_result.get("reason", "")
    direction = event_data.get("direction", "unknown")
    approach = event_data.get("approach", "closing")

    # Topological spatial awareness
    node_status = tools.get_node_status(node_id)
    next_node = tools.predict_next_node(node_id)
    recent_events = tools.get_recent_events(node_id)

    client, model_name, provider = get_llm_client()

    if client:
        try:
            logger.info(f"[Agent] Prompting {provider.upper()} ({model_name}) for tactical mitigation...")

            system_prompt = (
                "You are the WildWatch Autonomous Incident Orchestrator powered by NVIDIA Nemotron.\n"
                "Your mission: Prevent human-wildlife encounters at forest boundaries while safeguarding wild animals.\n"
                "Analyze the verified species, hazard level, camera node location, and movement trajectory.\n\n"
                "Key Rules:\n"
                "1. Non-harmful deterrents ONLY: Light strobe (level 1-3) and acoustic beeps/chirps (level 1-2).\n"
                "2. Directional safety: Never push an animal toward a village or human settlement.\n"
                "3. Multi-language alerts: Provide plain-language alerts in BOTH English and Hindi for forest guards and village panchayats.\n"
                "4. Output format: You must return ONLY a JSON array of action objects with no markdown formatting or intro.\n\n"
                "Expected JSON format:\n"
                "[\n"
                '  {"type": "deterrent", "action": "strobe", "level": 2, "target_node": "node-b"},\n'
                '  {"type": "alert", "message": "ALERT: Elephant approaching path. Strobe activated. / चेतावनी: हाथी रास्ते की ओर आ रहा है।"}\n'
                "]"
            )

            user_prompt = (
                f"Incident Telemetry:\n"
                f"- Event ID: {event_id}\n"
                f"- Sensor Node: {node_id}\n"
                f"- Verified Species: {species} (Confidence: {conf:.2f})\n"
                f"- Threat Assessment: {hazard_level.upper()}\n"
                f"- Biologist Diagnosis: {vlm_reason}\n"
                f"- Movement Vector: {direction} | Spatial Approach: {approach}\n"
                f"- Downstream Node: {next_node}\n"
                f"- Recent Node History: {len(recent_events)} sightings in last 2 hours\n\n"
                "Formulate the optimal tactical action plan:"
            )

            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
                max_tokens=400
            )

            raw_plan = response.choices[0].message.content.strip()
            if raw_plan.startswith("```"):
                raw_plan = raw_plan.strip("`").removeprefix("json").strip()

            actions = json.loads(raw_plan)
            logger.info(f"[Nemotron Decision Generated]: {actions}")
            return actions

        except Exception as e:
            logger.warning(f"[Agent] Cloud LLM call failed ({e}). Falling back to NVIDIA Nemotron rule engine.")

    # High-Fidelity NVIDIA Nemotron Rule Engine (Simulated Mode)
    actions = []
    
    # Hindi name translations
    hindi_species = {
        "elephant": "हाथी (Elephant)",
        "leopard": "तेंदुआ (Leopard)",
        "tiger": "बाघ (Tiger)",
        "bear": "भालू (Bear)",
        "sloth_bear": "रीछ / भालू (Sloth Bear)",
        "wild_boar": "जंगली सुअर (Wild Boar)",
        "nilgai": "नीलगाय (Nilgai)",
        "deer": "हिरण (Deer)",
        "monkey": "बंदर (Monkey)",
        "cattle": "मवेशी (Cattle)"
    }.get(species.lower(), species)

    if hazard_level == "high":
        # Dangerous predator or elephant moving towards boundary
        target_deterrent_node = next_node if next_node != "node_unknown" else node_id
        actions.append({
            "type": "deterrent",
            "action": "strobe",
            "level": 3,
            "target_node": target_deterrent_node,
            "reason": f"High intensity strobe deployed at {target_deterrent_node} to divert {species} from settlement path."
        })
        actions.append({
            "type": "deterrent",
            "action": "sound",
            "level": 2,
            "target_node": node_id,
            "reason": "Acoustic deterrent active to discourage forward movement."
        })
        actions.append({
            "type": "alert",
            "hazard": "high",
            "message": (
                f"🚨 CRITICAL WILDLIFE ALERT [{node_id.upper()}]\n"
                f"Verified: {species.upper()} moving {direction} ({approach}).\n"
                f"Predicted corridor towards {next_node}.\n"
                f"Actions: Strobe Level 3 & Sound Deterrents triggered at forest border.\n\n"
                f"📢 चेतावनी: {node_id.upper()} के पास {hindi_species} देखा गया है। वन मार्ग से दूर रहें और सुरक्षित स्थान पर रहें।"
            )
        })
    elif hazard_level == "medium":
        actions.append({
            "type": "deterrent",
            "action": "sound",
            "level": 1,
            "target_node": node_id,
            "reason": f"Mild acoustic deterrent pulse for {species}."
        })
        actions.append({
            "type": "alert",
            "hazard": "medium",
            "message": (
                f"⚠️ CAUTION NOTICE [{node_id.upper()}]: {species.capitalize()} detected near boundary.\n"
                f"Movement: {direction}. Mild acoustic deterrent active.\n\n"
                f"📢 सूचना: {node_id.upper()} पर {hindi_species} देखा गया है। सतर्क रहें।"
            )
        })
    elif hazard_level == "low":
        actions.append({
            "type": "deterrent",
            "action": "strobe",
            "level": 1,
            "target_node": node_id,
            "reason": "Low-intensity beacon active."
        })
        actions.append({
            "type": "alert",
            "hazard": "low",
            "message": f"ℹ️ INFO: Low-hazard animal ({species}) observed at {node_id}. Logged for wildlife census."
        })
    else:
        logger.info(f"[Nemotron Agent] No action needed for benign observation ({species}).")

    return actions
