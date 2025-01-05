from dataclasses import dataclass
from typing import Optional


@dataclass
class DetectedActionMessage:
    listener_id: str
    listener_name: str
    listener_type: str
    action_detected: dict
    action_data: Optional[dict] = None


@dataclass
class ListenerHeartbeatMessage:
    listener_id: str
