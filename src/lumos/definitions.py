import os

ROOT_DIR = "/".join(__file__.split("/")[0:-3])
CONF_DIR = os.path.join(ROOT_DIR, "configs")
LOG_DIR = os.path.join(ROOT_DIR, "logs")
MODELS_DIR = os.path.join(ROOT_DIR, "models")