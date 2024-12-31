from argparse import ArgumentParser


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
    action_listener.config(args.config)
    action_listener.start()
