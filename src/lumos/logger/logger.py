from src.lumos.definitions import LOG_DIR
import os
import logging.config

long_conf_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "logging.conf")
os.chdir(LOG_DIR)  ## import to ensure that logs are written in LOG_DIR

if not os.path.exists(long_conf_file):
    raise Exception(f"File {os.path.abspath(long_conf_file)} does not exist")

logging.config.fileConfig(long_conf_file)

