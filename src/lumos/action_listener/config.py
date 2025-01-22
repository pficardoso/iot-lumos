from typing import Literal, Union

from pydantic import BaseModel


class HttpProtocolConfig(BaseModel):
    type: Literal["http"]
    led_controller_address: str
    led_controller_port: int


class MqttProtocolConfig(BaseModel):
    type: Literal["mqtt"]
    broker_address: str
    broker_port: int


class BaseActionListenerConfig(BaseModel):
    """
    No need for a name. If you change the listener to another
    location you have to change the config everytime. Let's change that
    only in the led controller cofig file
    """

    id: str
    type: str
    protocol: Union[HttpProtocolConfig, MqttProtocolConfig]
