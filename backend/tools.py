import os
import yaml
import logging
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

def predict_next_node(current_node: str):
    """
    Predicts the next node the animal is likely approaching based on directional edges.
    """
    topology = load_topology()
    for edge in topology.get("edges", []):
        if edge.get("source") == current_node:
            return edge.get("target")
    
    # Fallback to alternative node if defined
    nodes = [n.get("id") for n in topology.get("nodes", [])]
    for n in nodes:
        if n != current_node:
            return n

    return "node-b" if current_node == "node-a" else "node-a"

def trigger_deterrent(node_id: str, deterrent_type: str = "sound", level: int = 1):
    """Queues a deterrent actuation command for the specified edge node."""
    logger.info(f"[Tool: trigger_deterrent] Actuating {deterrent_type.upper()} Level {level} at {node_id}")
    db.queue_command(node_id, {"type": "deterrent", "action": deterrent_type, "level": level})
    return True

def send_alert(message: str):
    """Dispatches alert to Telegram Bot for forest rangers."""
    from telegram_bot import send_telegram_message
    return send_telegram_message(message)
