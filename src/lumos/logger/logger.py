import logging.config
import os

from lumos.definitions import Definitions

definitions = Definitions()

long_conf_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "logging.conf"
)
os.makedirs(definitions.log_dir, exist_ok=True)

if not os.path.exists(long_conf_file):
    raise Exception(f"File {os.path.abspath(long_conf_file)} does not exist")

logging.config.fileConfig(long_conf_file)
