import logging.config
from src.lumos.definitions import CONF_DIR, LOG_DIR
import os

os.chdir(LOG_DIR)  ## import to ensure that logs are written in LOG_DIR

conf_file = "/".join([CONF_DIR, "logging.conf"])
if not os.path.exists(conf_file):
    raise Exception(f"File {os.path.abspath(conf_file)} does not exist")

logging.config.fileConfig(conf_file)

