from lumos.common.messages import LedCommandMessage
from lumos.definitions import Definitions
from lumos.led_controller.led_controller import LedController

definitions = Definitions()


class RhasspyHelper:
    RHASSPY_INTENT_FILTER = "hermes/intent/#"
    LISTENER_ID = "rhasspy"
    LISTENER_NAME = "rhasspy"
    LISTENER_TYPE = "rhasspy"

    def __init__(self):
        self.map_rhasspy_intent_to_led_command = {
            "ToggleLight": LedController.TOGGLE_ACTION,
            "ChangeLightColor": LedController.CHANGE_COLOR_ACTION,
            "ChangeLightBrightness": LedController.CHANGE_BRIGHTNESS_ACTION,
        }

    def convert_intent_mqtt_to_led_command_msg(
        self, intent_msg: dict
    ) -> LedCommandMessage:
        try:
            intent_name: str = intent_msg["intent"]["intentName"]
            slots: dict = {
                slot["slotName"]: slot["value"]["value"] for slot in intent_msg["slots"]
            }
            target_led = slots.pop("light_name")
        except Exception:
            raise ValueError(f"Error parsing intent message {intent_msg}")

        # validate that command exists
        if intent_name not in self.map_rhasspy_intent_to_led_command.keys():
            raise KeyError(
                f"Convertion for intent '{intent_name}' is not available. "
                f"Available intent are: {self.map_rhasspy_intent_to_led_command.keys()}"
            )

        lumos_target_command = self.map_rhasspy_intent_to_led_command[intent_name]

        lumos_command_args = None
        # adapt command args based on the command selected
        try:
            if lumos_target_command == LedController.TOGGLE_ACTION:
                lumos_command_args = None
            elif lumos_target_command == LedController.CHANGE_COLOR_ACTION:
                lumos_command_args = self.get_change_color_args(slots)
            elif lumos_target_command == LedController.CHANGE_BRIGHTNESS_ACTION:
                lumos_command_args = self.get_change_brightness_args(slots)
        except Exception:
            raise ValueError(
                f"Error parsing command arguments from intent message {intent_msg}"
            )

        return LedCommandMessage(
            listener_id=self.LISTENER_ID,
            listener_name=self.LISTENER_NAME,
            listener_type=self.LISTENER_TYPE,
            target_led=target_led,
            command=lumos_target_command,
            command_args=lumos_command_args,
        )

    def get_change_brightness_args(self, slots: dict) -> dict:
        brightness = slots["brightness"]
        return {"brightness": brightness}

    def get_change_color_args(self, slots: dict) -> dict:
        color = slots["color"]
        rgb = definitions.colors_rgb_map[color]
        return {"rgb_color": rgb}
