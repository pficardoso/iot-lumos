from typing import Union

from pydantic import BaseModel, validator


class HttpProtocolConfig(BaseModel):
    type: str = "http"
    led_controller_address: str
    led_controller_port: int

    @validator("type")
    def validate_type(cls, value):
        if value != "http":
            raise ValueError("The 'type' field must be 'http'.")
        return value


class MqttProtocolConfig(BaseModel):
    type: str = "mqtt"
    broker_address: str
    broker_port: int

    @validator("type")
    def validate_type(cls, value):
        if value != "mqtt":
            raise ValueError("The 'type' field must be 'mqtt'.")
        return value


class BaseActionListenerConfig(BaseModel):
    """
    No need for a name. If you change the listener to another
    location you have to change the config everytime. Let's change that
    only in the led controller cofig file
    """

    id: str
    type: str
    protocol: Union[HttpProtocolConfig, MqttProtocolConfig]
