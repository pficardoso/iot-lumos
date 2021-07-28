


class ConfigChecker():

    _mandatory_fields = ["id", "type", "led_controller_ip"]

    def __init__(self):
        pass

    def check_config_data(self, config_data:dict):

        mandatory_check = self._check_config_mandatory_fields(config_data)
        fields_value_types_check = self._check_fields_valus_type(config_data)

        return (mandatory_check and fields_value_types_check)

    def _check_config_mandatory_fields(self, config_data:dict) -> bool:

        check_flag = True
        fields_not_exist = set()
        for field in ConfigChecker._mandatory_fields:
            if field not in config_data.keys():
                fields_not_exist.add(field)
                check_flag = False


        if len(fields_not_exist) != 0:
            raise Exception(f"The following mandatory fields do not exist: {fields_not_exist}")

        return check_flag

    def _check_fields_valus_type(self, config_data:dict) -> bool:

        check_flag = True
        if "led_controller_port" in config_data:
            try:
                value = int(config_data["led_controller_port"])
            except ValueError:
                check_flag = False
                raise Exception("The value of led_controller_port should be an int")

        return check_flag




