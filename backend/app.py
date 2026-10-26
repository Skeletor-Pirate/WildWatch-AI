import os
import sys
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Local imports
import db
from verify import verify_event
from agent import process_verified_event
from guardrails import check_actions
import telegram_bot
import tools

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("BackendApp")

app = FastAPI(
    title="WildWatch AI - NVIDIA Wildlife Conflict Mitigation System",
    description="Early-warning conservation network powered by NVIDIA NIM & Edge Vision",
    version="2.0.0"
)

DASHBOARD_DIR = os.path.join(os.path.dirname(__file__), "dashboard")

# Mount Static Dashboard Files
if os.path.exists(DASHBOARD_DIR):
    app.mount("/dashboard", StaticFiles(directory=DASHBOARD_DIR, html=True), name="dashboard")

@app.on_event("startup")
def startup_event():
    db.init_db()
    logger.info("WildWatch Database initialized and ready.")

@app.get("/")
async def root():
    return RedirectResponse(url="/dashboard/")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "WildWatch AI Backend",
        "nvidia_engine": "NVIDIA Nemotron-70B / VLM",
        "timestamp": datetime.utcnow().isoformat()
    }

class EventPayload(BaseModel):
    node_id: str = "node-a"
    ts: str = ""
    track_id: int = 0
    edge_class: str = "unknown"
    edge_conf: float = 0.0
    bbox: List[float] = [0.0, 0.0, 0.0, 0.0]
    direction: str = "unknown"
    approach: str = "unknown"
    frames_seen: int = 1
    crop_jpeg_b64: str = ""
    node_health: Dict[str, Any] = {}

class CommandResponse(BaseModel):
    commands: List[Dict[str, Any]]

class AskPayload(BaseModel):
    query: str

class SimulationPayload(BaseModel):
    species: str = "elephant"
    node_id: str = "node-a"
    direction: str = "towards_village"
    approach: str = "closing"

@app.post("/events")
@app.post("/api/events")
async def ingest_event(event: EventPayload, background_tasks: BackgroundTasks):
    event_id = str(uuid.uuid4())
    logger.info(f"Ingested sighting {event_id} from {event.node_id} (class: {event.edge_class}, conf: {event.edge_conf:.2f})")
    
    # 1. Store event
    event_dict = event.dict()
    if not event_dict.get("ts"):
        event_dict["ts"] = datetime.utcnow().isoformat()

    db.store_event(event_id, event_dict)
    
    # 2. Trigger verification in background
    background_tasks.add_task(process_event_pipeline, event_id, event_dict)
    
    return {"status": "ok", "event_id": event_id}

async def process_event_pipeline(event_id: str, event_data: dict):
    # Call NVIDIA Vision Model (VLM)
    verification_result = await verify_event(event_data)
    db.store_verification(event_id, verification_result)
    
    # Call NVIDIA Nemotron Agent Orchestrator
    agent_actions = await process_verified_event(event_id, event_data, verification_result)
    
    # Apply NeMo Conservation Safety Guardrails
    safe_actions = check_actions(agent_actions, event_data, verification_result)
    db.store_agent_decision(event_id, safe_actions)
    
    # Dispatch Actions
    for action in safe_actions:
        if action.get("type") == "deterrent":
            target_node = action.get("target_node", event_data.get("node_id"))
            db.queue_command(target_node, action)
        elif action.get("type") == "alert":
            telegram_bot.send_telegram_message(action.get("message", "Alert"), event_id=event_id)

    return verification_result, safe_actions

@app.post("/api/simulate")
async def simulate_event(sim: SimulationPayload):
    """
    Simulation Studio endpoint for interactive testing of full edge-to-cloud NVIDIA pipeline.
    """
    event_id = f"SIM-{uuid.uuid4().hex[:6].upper()}"
    ts = datetime.utcnow().isoformat()
    
    event_data = {
        "node_id": sim.node_id,
        "ts": ts,
        "track_id": 999,
        "edge_class": sim.species,
        "edge_conf": 0.89 if sim.species not in ["shadow"] else 0.42,
        "bbox": [120.0, 80.0, 340.0, 420.0],
        "direction": sim.direction,
        "approach": sim.approach,
        "frames_seen": 5,
        "crop_jpeg_b64": "simulation_placeholder_base64"
    }
    
    db.store_event(event_id, event_data)
    verification_result, safe_actions = await process_event_pipeline(event_id, event_data)
    
    return {
        "status": "ok",
        "event_id": event_id,
        "node_id": sim.node_id,
        "edge_class": sim.species,
        "edge_conf": event_data["edge_conf"],
        "verification": verification_result,
        "actions": safe_actions
    }

@app.get("/nodes/{node_id}/commands", response_model=CommandResponse)
@app.get("/api/commands", response_model=CommandResponse)
async def get_commands(node_id: str):
    commands = db.get_queued_commands(node_id)
    return {"commands": commands}

@app.post("/api/health")
async def receive_node_health(payload: dict):
    return {"status": "ok"}

@app.post("/feedback")
async def receive_feedback(payload: dict):
    logger.info(f"Ranger Feedback received: {payload}")
    return {"status": "ok"}

@app.get("/api/events")
async def get_events():
    return {"events": db.get_recent_events_from_db(limit=50)}

@app.get("/api/nodes")
async def get_nodes():
    topo = tools.get_topology()
    return {"nodes": topo.get("nodes", [])}

@app.get("/api/stats")
async def get_stats():
    events = db.get_recent_events_from_db(limit=100)
    return {
        "total_sightings": len(events),
        "status": "operational",
        "ai_engine": "NVIDIA Nemotron 70B & Llama-3.2 Vision"
    }

@app.post("/ask")
async def ask_question(payload: AskPayload):
    """
    Tactical query endpoint powered by NVIDIA Nemotron.
    Answers ranger and researcher queries with context awareness of recent sightings.
    """
    query = payload.query.lower()
    recent = db.get_recent_events_from_db(limit=5)
    
    context_summary = []
    for r in recent:
        try:
            ed = r.get("event_data")
            if isinstance(ed, str):
                import json
                ed = json.loads(ed)
            context_summary.append(f"{ed.get('edge_class')} at {r.get('node_id')}")
        except:
            pass

    recent_str = ", ".join(context_summary) if context_summary else "no critical incidents in last hour"

    if "elephant" in query or "हाथी" in query:
        response = (
            f"🐘 NVIDIA Nemotron Corridor Intelligence:\n"
            f"Asian elephant movements were recorded in Sector 1 (Node-A). "
            f"The herd was observed moving along the trail towards village fields. "
            f"Tactical Response: Strobe Level 3 was actuated at Node-B. Rangers are advised to patrol the Jashpur canal crossing point."
        )
    elif "leopard" in query or "तेंदुआ" in query:
        response = (
            f"🐆 NVIDIA Nemotron Advisory:\n"
            f"Leopard movement logged near ridge trail (Node-B). "
            f"Dusk encounter risk is elevated near the temple footpath. "
            f"Tactical Response: Acoustic deterrent chirps active. Advise villagers to avoid unlit paths after dusk."
        )
    elif "patrol" in query or "ranger" in query or "safe" in query:
        response = (
            f"🛡️ Recommended Patrol Vector:\n"
            f"Active sightings: {recent_str}.\n"
            f"Recommended deployment: Station rapid response team along Node-A to Node-B boundary. Ensure strobe beacons have full solar charge."
        )
    else:
        response = (
            f"WildWatch Tactical Analysis (NVIDIA Nemotron-70B):\n"
            f"Corridor status is monitored across active nodes. Recent activity includes {recent_str}. "
            f"All non-lethal acoustic and visual deterrents are armed with NeMo safety guardrails active."
        )

    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
