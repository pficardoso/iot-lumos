import json
from argparse import ArgumentParser

from lumos.led_controller.config import (
    HttpProtocolConfig,
    LedControllerConfig,
    MqttProtocolConfig,
)


def add_arguments(parser: ArgumentParser):
    parser.add_argument(
        "-c",
        "--config",
        help="Config file of the led controller",
        required=True,
    )


def run(args):
    config_data = LedControllerConfig(**json.load(open(args.config)))
    if isinstance(config_data.protocol, MqttProtocolConfig):
        from lumos.led_controller.mqtt_client import start_led_controller_mqtt_client

        start_led_controller_mqtt_client(config_data)
    elif isinstance(config_data.protocol, HttpProtocolConfig):
        from lumos.led_controller.http_service import start_led_controller_http_service

        start_led_controller_http_service(config_data)
    else:
        raise Exception(f"Protocol {config_data.protocol} is not supported")
