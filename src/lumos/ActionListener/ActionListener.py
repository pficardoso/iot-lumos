import abc
import logging
import json
import requests
import src.lumos.logger
import threading
import time
from src.lumos.ActionListener.ConfigChecker import ConfigChecker

logger = logging.getLogger("action_listener")

class ActionListener(metaclass=abc.ABCMeta):
    """"""
    type="Base"
    name="Base"

    default_led_controller_port = 8000
    default_heartbeat_period = 660 #seconds
    heartbeat_endpoint = "/listener_heartbeat"

    def __init__(self,):
        """Constructor for ActionListener"""
        self.id = None
        self.type = "ActionListener"
        self.led_controller_ip = None
        self.led_controller_heartbeat_url = None
        self.led_controller_port = None
        self.configured = False
        self._config_checker = ConfigChecker()
        self._heartbeat_period = None #seconds
        self._heartbeat_thread = None

    """
    Setters/Loaders
    """
    def config(self, config_path) -> bool:

        with open(config_path, "r") as f_conf:
            config_data = json.load(f_conf)["action_listener"]

        is_configured_gen = self._config_general(config_data)
        is_configured_spe = self._config_specialized(config_data)

        self.configured = (is_configured_gen and is_configured_spe)
        return self.configured

    def _config_general(self, config_data:dict) -> bool:

        config_check_flag = self._config_checker.check_config_data(config_data)

        self.id = config_data["id"]
        self.type = config_data["type"]
        self.led_controller_port = int(config_data["led_controller_port"]) \
                                    if "led_controller_port" in config_data.keys() \
                                    else ActionListener.default_led_controller_port
        self.led_controller_ip = config_data["led_controller_ip"]
        self.led_controller_heartbeat_url = f"http://{self.led_controller_ip}:{self.led_controller_port}{ActionListener.heartbeat_endpoint}"
        self._heartbeat_period = int(config_data["heartbeat_period"]) \
                                if "heartbeat_period" in config_data.keys() \
                                else ActionListener.default_heartbeat_period

        return config_check_flag

    @abc.abstractmethod
    def _config_specialized(self, config_data:dict) -> bool:
        pass


    """
    Getters
    """

    """
    Workers
    """

    @abc.abstractmethod
    def _run_engine(self):
        pass

    def _run_heartbeats_mechanism(self):

        def heartbeats_mechanism(period):
           while True:
                time.sleep(period)
                logger.info("Sending heartbeat to led controller")
                if self._check_connection_led_controller():
                    logger.info("Heartbeat sent with success")
                else:
                    logger.error("Heartbeat was sent unsuccessfully")


        self._heartbeat_thread = threading.Thread(target=heartbeats_mechanism, args=(self._heartbeat_period,), daemon=True)
        self._heartbeat_thread.start()

    def _send_detected_action(self, action_name, action_params=None):

        item = {"action": action_name}
        if action_params:
            if not isinstance(action_params, dict):
                raise Exception(f"action_params should be a dict - {type(action_params)}  was given")
        item["action_param"] = action_params

        request_data = dict()
        request_data["id"]=self.id
        request_data["listener_action"]=item["action"]
        target_url = f"http://{self.led_controller_ip}:{self.led_controller_port}/listener_request"
        try:
            r = requests.post(target_url,
                              data=json.dumps(request_data),
                              timeout=0.2)
        except Exception as e:
            logger.error(f"Error while doing request to led controller - Message error: {e}")
        else:
            logger.info(f"Send with success the detected action to {target_url} with data {request_data}")
        ## TODO: check response and report on log

    def start(self):

        logger.info(f"Starting {self.name}...")
        if not self.configured:
            logger.error(f"Could not start {self.name}. Not configured")
            raise Exception("Not configured")

        if not self._check_connection_led_controller():
            msg = f"Could not connect with led controller, with ip address {self.led_controller_ip}"
            logger.error(msg)
            raise Exception(msg)

        self._run_engine() #starts the thread of engine
        self._run_heartbeats_mechanism()
        logger.info(f"{self.name} started")


    """
    Boolean methods
    """

    """
    Checkers
    """
    def _check_connection_led_controller(self):

        data = {"id":self.id}

        try:
            response = requests.post(self.led_controller_heartbeat_url,data=json.dumps(data))
        except requests.exceptions.ConnectionError:
            return False

        status_code = response.status_code
        return (status_code == 200)

    """
    Util methods / Static methods
    """

