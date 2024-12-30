from argparse import ArgumentParser

from lumos.LedController import start_led_controller_web_service

parser = ArgumentParser()
parser.add_argument("-c", "--config", help="Config file of led controller")

args = parser.parse_args()
start_led_controller_web_service(args.config)
