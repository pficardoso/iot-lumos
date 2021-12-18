import logging
import src.lumos.logger
import numpy
from src.lumos.ActionListener.ActionListener import ActionListener
from MAAP import AudioSignal, AudioFeatureExtractor
from MAAP.utils import audio_feature_2_tensor
import os
import queue
import numpy as np
import json
import tensorflow.keras as K
import sounddevice as sd
import sys

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
logger = logging.getLogger("action_listener")

class Model():

    def __init__(self):
        self.model_path = None
        self.model = None
        self.nr_segments = None
        self.tensors = None
        self.tensor_ndim = None
        self.configured = False

    def config(self, model_path, nr_segments, tensor_ndim=1):
        self.model_path = model_path
        self.model = K.models.load_model(self.model_path)
        self.nr_segments = nr_segments
        self.tensor_ndim = tensor_ndim
        self.configured = True

    def all_segments_exist(self):
        return len(self.tensors) == self.nr_segments

    def predict(self, segments_features):

        prob_prediction = 0
        if len(segments_features) == self.nr_segments:
            tensors = list()
            for s_ft in segments_features:
                tensor = audio_feature_2_tensor(s_ft,ndim=self.tensor_ndim)
                tensors.append(tensor)

            # obtain the input of the model
            self.input_x_model = np.concatenate(tensors)
            prob_prediction = self.model.predict(np.array([self.input_x_model]))

        return prob_prediction


class HandClapDetector(ActionListener):
    """"""
    name = "HandClapDetector"
    type = "HandClapDetector"

    def __init__(self,):
        """Constructor for HandClapDetector"""
        ActionListener.__init__(self)
        self._model_art_path  = None
        self._model_conf_path = None
        self._model        = Model()
        self._ft_extractor = AudioFeatureExtractor()
        self._audio_receiver = sd.InputStream()
        self._nr_segments = 0
        self._segments_duration = 0
        self._nr_samples_per_segment = 0
        self._sample_rate = 0
        self._model_input_ndim = 0
        self._audio_fts_list = list()
        self._audio_fts_params = dict()
        self._audio_buffer = numpy.empty((0,1))
        self._segments_queue = queue.Queue()
        self._features_queue = queue.Queue()
        self._detection_enabled = True
        self._it_counter = 0

    """
    Setters/Loaders
    """
    def _config_specialized(self, config_data:dict) -> bool:
        config_check_flag = self._config_checker.check_config_data(config_data, self.type)
        self._model_art_path = config_data["model_artifact_path"]
        self._model_conf_path     = config_data["model_conf_path"]

        logger.info(f"Configured with {self.name} with model {self._model_art_path}, using the configuration defined in"
                    f"{self._model_conf_path}")

        model_config_check_flag = self._check_model_config_data() #TODO: this function always return True
        if not model_config_check_flag:
            raise Exception(f"Model config data in {os.path.realpath(self._model_conf_path)} is not valid")

        with open(self._model_conf_path, "r") as json_file:
            confs = json.load(json_file)

        self._nr_segments       = confs["model"]["audio_params"]["nr_segments"]
        self._segments_duration = confs["model"]["audio_params"]["segment_duration"]
        self._features_queue = queue.Queue(maxsize=self._nr_segments)

        if "tensor_ndim" in confs["model"]:
            self._model_input_ndim = confs["model"]["tensor_ndim"]
        else:
            self._model_input_ndim = 1

        self._audio_fts_list    = confs["maap_audio_feature_extractor"]["features"]
        self._audio_fts_params  = confs["maap_audio_feature_extractor"]["features_func_args"]


        self._ft_extractor.config(self._audio_fts_list, **self._audio_fts_params)
        self._model.config(self._model_art_path, self._nr_segments, self._model_input_ndim)

        audio_device_id = sd.default.device[0]
        audio_device_info = sd.query_devices(audio_device_id, "input")

        self._sample_rate = audio_device_info["default_samplerate"]
        self._nr_samples_per_segment = int(self._sample_rate*self._segments_duration)
        self._audio_receiver = sd.InputStream(samplerate=self._sample_rate,
                                              device=audio_device_id,
                                              channels=1,
                                              callback=self._audio_receiver_callback)

        return all([model_config_check_flag, config_check_flag])

    def put_segment_features(self, features):
        if self._features_queue.full():
            self._features_queue.get()
        self._features_queue.put(features)

    def get_segments_features(self):
        return self._features_queue.queue

    def flush_segments_features(self):
        self._features_queue.queue.clear()

    """
    Getters
    """

    """
    Workers
    """

    def _audio_receiver_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self._audio_buffer = numpy.concatenate((self._audio_buffer, indata), axis=0)
        if self._audio_buffer.shape[0] > self._nr_samples_per_segment:
            y, new_buffer = numpy.split(self._audio_buffer, [self._nr_samples_per_segment], axis=0)
            signal = AudioSignal(y[:, 0], sample_rate=self._sample_rate)
            self._segments_queue.put(signal)
            self._audio_buffer = np.copy(new_buffer)
        else:
            pass


    def _run_engine(self):
        print("Listening and Predicting...")
        with self._audio_receiver:
            while True:
                segment = self._segments_queue.get()
                if self._detection_is_enabled():
                    ## compute feature
                    self._ft_extractor.load_audio_signal(segment)
                    segment_features = self._ft_extractor.compute_features_by_config()
                    self.put_segment_features(segment_features)
                    features = self.get_segments_features()
                    prob = self._model.predict(features)
                    if prob >= 0.8:
                        logger.info("Detected clap")
                        self._send_detected_action("clap_detected")
                        self._detection_enabled = False
                        self.flush_segments_features() ## these features are not going to be used anymore
                        logger.info("Detection suspended after clap being detected")
                else:
                    self._it_counter+=1
                    if self._it_counter == self._nr_segments:
                        self._detection_enabled = True
                        self._it_counter = 0
                        logger.info("Detection reactivated")





    """
    Boolean methods
    """
    def _detection_is_enabled(self):
        return self._detection_enabled

    """
    Checkers
    """
    def _check_model_config_data(self):
        #TODO: to improve
        # acess self._model_conf_path
        return True

    """
    Util methods / Static methods
    """

