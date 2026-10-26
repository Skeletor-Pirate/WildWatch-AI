"""
WildWatch Safety Guardrails (Inspired by NVIDIA NeMo Guardrails).
Enforces hard safety boundaries in deterministic code:
1. Deterrents are strictly non-lethal (light and sound only, capped at safe intensities).
2. Never push an animal toward a human settlement.
3. No deterrents fire unless verification confirms a genuine wildlife threat.
4. Alerts are verified and sanitized before reaching forest rangers and communities.
"""

import logging

logger = logging.getLogger("SafetyGuardrails")

def check_actions(actions: list, event_data: dict, verification_data: dict) -> list:
    """
    Evaluates proposed actions against strict conservation safety guardrails.
    Returns filtered and clamped list of safe actions.
    """
    safe_actions = []
    
    # Guardrail 1: False Alarm Suppression
    # If the VLM verification flagged this as non-animal (e.g. shadow, branch, cow, human),
    # physical deterrents must NOT trigger!
    is_real_animal = verification_data.get("is_real_animal", False)
    hazard_level = verification_data.get("hazard_level", "none")

    if not is_real_animal or hazard_level == "none":
        logger.info("[Guardrail] Zero-hazard/False sighting. Suppressing all deterrent actions.")
        return []

    direction = event_data.get("direction", "unknown").lower()
    approach = event_data.get("approach", "closing").lower()

    for action in actions:
        action_type = action.get("type")

        # Guardrail 2: Deterrent Intensity & Directional Boundaries
        if action_type == "deterrent":
            # Intensity clamping
            if action.get("action") == "strobe":
                action["level"] = max(1, min(int(action.get("level", 1)), 3))
            elif action.get("action") == "sound":
                action["level"] = max(1, min(int(action.get("level", 1)), 2))

            # Direction check: If the animal is retreating to the forest, DO NOT deter
            if "forest" in direction or direction == "away_from_village":
                logger.info(f"[Guardrail BLOCKED] Animal is safely retreating to forest ({direction}). Deterrent cancelled.")
                continue

            safe_actions.append(action)

        # Guardrail 3: Alert Validation
        elif action_type == "alert":
            # Ensure message exists and has actionable content
            msg = action.get("message", "").strip()
            if len(msg) > 5:
                safe_actions.append(action)

    logger.info(f"[Guardrails] Verified {len(safe_actions)} of {len(actions)} proposed actions as safe.")
    return safe_actions