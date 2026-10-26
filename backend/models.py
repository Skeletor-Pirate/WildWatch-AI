from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

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
    node_health: Dict[str, Any] = Field(default_factory=dict)

class VerificationResult(BaseModel):
    species: str
    confidence: float
    is_real_animal: bool
    hazard_level: str
    reason: str

class ActionItem(BaseModel):
    type: str  # "deterrent" or "alert"
    action: Optional[str] = None  # "strobe" or "sound"
    level: Optional[int] = None   # 1, 2, 3
    message: Optional[str] = None
