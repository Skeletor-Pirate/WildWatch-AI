import os
import sys
import yaml
import logging

sys.path.insert(0, os.path.dirname(__file__))
import db

logger = logging.getLogger("BackendTools")

TOPOLOGY_PATH = os.path.join(os.path.dirname(__file__), "topology.yaml")

def load_topology():
    if os.path.exists(TOPOLOGY_PATH):
        try:
            with open(TOPOLOGY_PATH, "r") as f:
                return yaml.safe_load(f) or {"nodes": [], "edges": []}
        except Exception as e:
            logger.warning(f"Error loading topology: {e}")
    return {"nodes": [], "edges": []}

def get_topology():
    """Returns the network topology containing sensor nodes and connecting edges."""
    return load_topology()

def get_recent_events(node_id=None, limit=5):
    """Fetches recent events from SQLite database for context awareness."""
    try:
        events = db.get_recent_events_from_db(node_id=node_id, limit=limit)
        return events
    except Exception as e:
        logger.warning(f"Error fetching recent events: {e}")
        return []

def get_node_status(node_id: str):
    """Returns the operational status and battery/signal health of a node."""
    topology = load_topology()
    for n in topology.get("nodes", []):
        if n.get("id") == node_id:
            return {
                "id": node_id,
                "status": "online",
                "location": n.get("location", "Sector Boundary"),
                "lat": n.get("lat"),
                "lon": n.get("lon"),
                "max_deterrent_level": n.get("max_deterrent_level", 3)
            }
    return {"id": node_id, "status": "online", "location": "General Sector"}

# Direction vocabulary shared with node/direction.py and guardrails.py
FOREST_DIRECTIONS = {"towards_forest", "away_from_village", "retreating"}
VILLAGE_DIRECTIONS = {"towards_village", "towards_crops", "towards_highway", "towards_water"}


def predict_corridor(current_node: str, direction: str = "unknown", approach: str = "unknown"):
    """
    Predicts where an animal seen at `current_node` is going, using its measured
    direction (not just the static topology).

    Returns:
      next_node   - downstream node it is heading to, or None if leaving the network
      heading     - retreating_to_forest | towards_village | along_corridor | unknown
      eta_sec     - typical travel time along the edge, or None
      confidence  - 0..1 heuristic
      reason      - human-readable explanation (used in alerts)
    """
    topology = load_topology()
    d = (direction or "unknown").lower()
    a = (approach or "unknown").lower()
    edges = [e for e in topology.get("edges", []) if e.get("source") == current_node]
    nodes = [n.get("id") for n in topology.get("nodes", []) if n.get("id") != current_node]

    if d in FOREST_DIRECTIONS:
        # Retreating: the next node is the neighbour on the forest side, if there is one.
        pos = {n.get("id"): n.get("corridor_position") for n in topology.get("nodes", [])}
        here = pos.get(current_node)
        behind = [e for e in edges if here is not None and pos.get(e.get("target")) is not None
                  and pos[e["target"]] < here]
        return {
            "next_node": behind[0].get("target") if behind else None,
            "heading": "retreating_to_forest",
            "eta_sec": behind[0].get("typical_travel_time_sec") if behind else None,
            "confidence": 0.8,
            "reason": "Animal is moving back toward deep forest; deterrents are withheld (anti-trap rule).",
        }

    # Pick the downstream neighbour in the direction of travel using each node's
    # corridor_position (0 = forest side, 1 = village side).
    positions = {n.get("id"): n.get("corridor_position") for n in topology.get("nodes", [])}
    here = positions.get(current_node)
    heading_village = d in VILLAGE_DIRECTIONS

    edge = None
    if here is not None and heading_village:
        ahead = [e for e in edges if positions.get(e.get("target")) is not None
                 and positions[e["target"]] > here]
        if ahead:
            edge = min(ahead, key=lambda e: positions[e["target"]])
        else:
            # Already at the village end of the corridor: nothing downstream.
            return {
                "next_node": None,
                "heading": "towards_village",
                "eta_sec": None,
                "confidence": 0.5,
                "reason": f"Animal heading toward the village from {current_node}; no further corridor node.",
            }
    elif edges:
        edge = edges[0]

    if edge:
        next_node = edge.get("target")
        eta = edge.get("typical_travel_time_sec")
    else:
        next_node = nodes[0] if nodes else None
        eta = None

    if heading_village:
        heading, confidence = "towards_village", 0.6
    else:
        heading, confidence = "along_corridor", 0.4

    if a == "closing":
        confidence = min(1.0, confidence + 0.2)

    reason = (
        f"Animal heading {heading.replace('_', ' ')} from {current_node}"
        + (f" toward {next_node}" if next_node else "")
        + (f" (ETA ~{eta}s)" if eta else "")
        + "."
    )
    return {
        "next_node": next_node,
        "heading": heading,
        "eta_sec": eta,
        "confidence": round(confidence, 2),
        "reason": reason,
    }


def predict_next_node(current_node: str, direction: str = "unknown"):
    """Backward-compatible wrapper: returns only the predicted next node."""
    return predict_corridor(current_node, direction)["next_node"]

def trigger_deterrent(node_id: str, deterrent_type: str = "sound", level: int = 1):
    """Queues a deterrent actuation command for the specified edge node."""
    logger.info(f"[Tool: trigger_deterrent] Actuating {deterrent_type.upper()} Level {level} at {node_id}")
    db.queue_command(node_id, {"type": "deterrent", "action": deterrent_type, "level": level})
    return True

def send_alert(message: str):
    """Dispatches alert to Telegram Bot for forest rangers."""
    from telegram_bot import send_telegram_message
    return send_telegram_message(message)
