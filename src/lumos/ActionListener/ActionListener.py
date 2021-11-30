import abc
import logging
import json
import queue
import requests
import lumos.logger
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
        self._detected_actions_queue = queue.Queue()

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

    def _add_detected_action(self, action_name:str, action_param=None):
        item = {"action":action_name}
        if action_param:
            if not isinstance(action_param, dict):
                raise Exception(f"action_params should be a dict - {type(action_param)}  was given")
            item["action_param"] = action_param

        self._detected_actions_queue.put(item)

    """
    Getters
    """

    """
    Workers
    """

    @abc.abstractmethod
    def _build_engine(self):
        pass

    @abc.abstractmethod
    def _start_engine(self):
        pass

    def _start_heartbeats_mechanism(self):

        def heartbeats_mechanism(period):
            start_time = time.time()
            while True:
                current_time = time.time()
                if (current_time - start_time) > period:
                    logger.info("Sending heartbeat to led controller")
                    start_time = current_time
                    if self._check_connection_led_controller():
                        logger.info("Heartbeat sent with success")
                    else:
                        logger.error("Heartbeat was sent unsuccessfully")


        self._heartbeat_thread = threading.Thread(target=heartbeats_mechanism, args=(self._heartbeat_period,), daemon=True)
        self._heartbeat_thread.start()

    def _start_process_actions_queue_mechanism(self):

        def mechanism():
            while True:
                detected_action_item = self._detected_actions_queue.get()
                self._send_detected_action(detected_action_item)
                self._detected_actions_queue.task_done()

        t = threading.Thread(target=mechanism)
        t.start()


    def _send_detected_action(self, item):
        request_data = {}
        request_data["id"]=self.id
        request_data["listener_action"]=item["action"]
        target_url = f"http://{self.led_controller_ip}:{self.led_controller_port}/listener_request"
        r = requests.post(target_url,
                      data=json.dumps(request_data))
        logger.info(f"Send detected action to {target_url} with data {request_data}")
        ## check response and report on log

    def start(self):

        logger.info(f"Starting {self.name}...")
        if not self.configured:
            logger.error(f"Could not start {self.name}. Not configured")
            raise Exception("Not configured")

        if not self._check_connection_led_controller():
            msg = f"Could not connect with led controller, with ip address {self.led_controller_ip}"
            logger.error(msg)
            raise Exception(msg)

        self._build_engine()
        self._start_engine() #starts the thread of engine
        self._start_heartbeats_mechanism()
        self._start_process_actions_queue_mechanism()
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

