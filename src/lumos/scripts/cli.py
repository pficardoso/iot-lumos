import argparse
import importlib

import lumos.logger  # noqa: F401


def main():
    parser = argparse.ArgumentParser(description="Lumos")
    subparsers = parser.add_subparsers(dest="command")

    for module_name in ["action_listener", "led_controller"]:
        module = importlib.import_module(f"lumos.scripts.{module_name}")
        subparser = subparsers.add_parser(module_name, prog=module_name)
        module.add_arguments(subparser)

    args = parser.parse_args()
    if args.command:
        module = importlib.import_module(f"lumos.scripts.{args.command}")
        module.run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
