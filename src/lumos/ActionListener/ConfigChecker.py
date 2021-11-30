class ConfigChecker():

    _mandatory_fields = ["id", "type", "led_controller_ip"]
    _mandatory_fields_timer = ["timer_period"]

    def __init__(self):
        self._mandatory_fields=None
        pass

    def check_config_data(self, config_data:dict, type="base"):

        if type == "base": self.mandatory_fields = ConfigChecker._mandatory_fields
        elif type == "Timer": self.mandatory_fields = ConfigChecker._mandatory_fields_timer
        else: raise Exception(f"Type {type} does not exist")

        mandatory_check = self._check_config_mandatory_fields(config_data)
        fields_value_types_check = self._check_fields_value_type(config_data, type)

        return (mandatory_check and fields_value_types_check)

    def _check_config_mandatory_fields(self, config_data:dict, type="base") -> bool:

        check_flag = True
        fields_not_exist = set()
        for field in self.mandatory_fields:
            if field not in config_data.keys():
                fields_not_exist.add(field)
                check_flag = False


        if len(fields_not_exist) != 0:
            raise Exception(f"The following mandatory fields do not exist: {fields_not_exist}")

        return check_flag

    def _check_fields_value_type(self, config_data:dict, type="base") -> bool:
        if type == "base":
            return self._check_fields_value_type_base(config_data)
        elif type == "Timer":
            return self._check_fields_value_type_timer(config_data)
        else:
            raise Exception(f"Type {type} does not exist")

    def _check_fields_value_type_base(self, config_data:dict) -> bool:

        check_flag = True
        if "led_controller_port" in config_data:
            try:
                value = int(config_data["led_controller_port"])
            except ValueError:
                check_flag = False
                raise Exception("The value of led_controller_port should be an int")

        return check_flag

    def _check_fields_value_type_timer(self, config_data:dict) -> bool:
        check_flag = True
        if "timer_period" in config_data:
            try:
                value = int(config_data["timer_period"])
            except ValueError:
                check_flag = False
                raise Exception("The value of timer_period should be an int")

        return check_flag

