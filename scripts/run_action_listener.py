from argparse import ArgumentParser

from lumos.action_listener import ActionListerCatalog

parser = ArgumentParser()
parser.add_argument("-c", "--config", help="Config file of led controller")

args = parser.parse_args()
action_listener = ActionListerCatalog().get_action_listener("Timer")
action_listener.config(args.config)
action_listener.start()
