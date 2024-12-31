from argparse import ArgumentParser


def add_arguments(parser: ArgumentParser):
    parser.add_argument(
        "-c",
        "--config",
        help="Config file of the led controller",
        required=True,
    )


def run(args):
    from lumos.led_controller import start_led_controller_web_service

    start_led_controller_web_service(args.config)
