from typing import Dict, List, Literal, Union

from pydantic import BaseModel, field_validator


class HttpProtocolConfig(BaseModel):
    type: Literal["http"]
    port: int


class MqttProtocolConfig(BaseModel):
    type: Literal["mqtt"]
    broker_address: str
    broker_port: int


class LedConfig(BaseModel):
    address: str


class ListenerConfig(BaseModel):
    id: str


class ListenerLedMapConfig(BaseModel):
    listener: str  # name of the listener
    led: str  # name of the led
    detected_action: str
    led_action: str


class LedControllerConfig(BaseModel):
    name: str
    leds: Dict[str, LedConfig]  # {led_name: Led}
    listeners: Dict[str, ListenerConfig]  # {listener_name: Listener}
    listener_led_map: List[ListenerLedMapConfig]
    protocol: Union[HttpProtocolConfig, MqttProtocolConfig]
    use_rhasspy: bool = False

    @field_validator("listener_led_map")
    def validate_listener_led_map(cls, v, info):
        values = info.data
        leds = values.get("leds", {})
        listeners = values.get("listeners", {})
        for listener_led_map_item in v:
            if listener_led_map_item.listener not in listeners:
                raise ValueError(
                    f"Listener '{listener_led_map_item.listener}' not found in listeners"
                )
            if listener_led_map_item.led not in leds:
                raise ValueError(f"LED '{listener_led_map_item.led}' not found in LEDs")
        return v
