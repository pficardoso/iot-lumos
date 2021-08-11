import logging.config
import os


conf_file = "configs/logging.conf"
if not os.path.exists(conf_file):
    raise Exception(f"File {os.path.abspath(conf_file)} does not exist")

logging.config.fileConfig(conf_file)

