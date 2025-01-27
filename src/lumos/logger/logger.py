import datetime
import logging.config
import os
import tempfile
from configparser import ConfigParser

from lumos.definitions import Definitions

definitions = Definitions()

long_conf_file = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "logging.conf"
)
configParser = ConfigParser()
configParser.read(long_conf_file)

current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
log_dir = os.path.join(definitions.log_dir, current_datetime)
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "lumos.log")

# Inject dynamic log file path into the configuration
configParser.set("handler_lumosFileHandler", "args", f"('{log_file}', 'w')")

# Write the updated configuration to a temporary file
tmp_file = tempfile.NamedTemporaryFile(
    mode="w", delete=False, suffix=".logging.conf", prefix="lumos."
)
configParser.write(tmp_file)
tmp_file.close()

# Load the logging configuration
logging.config.fileConfig(tmp_file.name)
