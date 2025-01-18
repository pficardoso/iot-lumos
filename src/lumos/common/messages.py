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
class LedCommandMessage:
    listener_id: Optional[str]
    listener_name: Optional[str]
    listener_type: Optional[str]
    target_led: str
    command : str
    command_args : Optional[dict]

@dataclass
class ListenerHeartbeatMessage:
    listener_id: str
