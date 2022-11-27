from lumos.ActionListener import ActionListerCatalog
from argparse import ArgumentParser
import os

parser = ArgumentParser()
parser.add_argument("-c","--config", help="Config file of led controller")

args = parser.parse_args()
action_listener = ActionListerCatalog().get_action_listener("Timer")
action_listener.config(args.config)
action_listener.start()
