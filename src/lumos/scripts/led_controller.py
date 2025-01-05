from argparse import ArgumentParser


def add_arguments(parser: ArgumentParser):
    parser.add_argument(
        "-c",
        "--config",
        help="Config file of the led controller",
        required=True,
    )


def run(args):
    from lumos.led_controller.http_service import start_led_controller_http_service

    start_led_controller_http_service(args.config)
