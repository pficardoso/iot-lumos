from src.lumos.definitions import Definitions
import os
import logging.config

definitions = Definitions()

long_conf_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logging.conf")
os.chdir(definitions.log_dir)  ## import to ensure that logs are written in LOG_DIR

if not os.path.exists(long_conf_file):
    raise Exception(f"File {os.path.abspath(long_conf_file)} does not exist")

logging.config.fileConfig(long_conf_file)

