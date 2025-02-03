import json
from argparse import ArgumentParser

from lumos.action_listener.config import TimerConfig


def add_arguments(parser: ArgumentParser) -> None:
    """Add command line arguments to parser."""
    parser.add_argument(
        "-c",
        "--config",
        help="Config file of the action listener",
        required=True,
    )


def run(args) -> None:
    """Run the action listener."""
    from lumos.action_listener import ActionListerCatalog

    catalog = ActionListerCatalog()
    action_listener = catalog.get_action_listener("Timer")
    config = TimerConfig(**json.load(open(args.config)))
    action_listener.config(config)
    action_listener.start()
