


class ConfigChecker():

    def __init__(self):
        pass


    def check_config_data(self, config_data:dict):
        # IMPROVEMENT: Break this function into steps. Consider to pass this logic to a new class, allowing the
        #    code reusability in other classes that require this logic during their configuration

        valid = True

        MANDATORY_FIELDS = ["name", "leds", "listeners", "listener_led_map"]

        # check if all mandatory fields exist
        missing_fields = MANDATORY_FIELDS.copy()
        for field in MANDATORY_FIELDS:
            if field in config_data.keys():
                missing_fields.remove(field)
        if len(missing_fields) != 0:
            valid = False
            raise Exception(f"Fields {missing_fields} are missing")

        led_valid = self.check_config_leds_field(config_data["leds"])
        listener_valid = self.check_config_listeners_field(config_data["listeners"])
        map_valid = self.check_config_listeners_led_map(config_data)

        # TODO: check if there are not collisions between mapping of led and listeners.
        #   Consider if you want to avoid this and launch Exception or just to launch a warning

        return (valid and led_valid and listener_valid and map_valid )


    def check_config_leds_field(self, config_data_leds:dict):

        valid = True
        led_names, led_ips, repeated_names, repeated_ips = set(), set(), set(), set()
        for led_name, led_ip in config_data_leds.items():

            if led_ip in led_ips:
                repeated_ips.add(led_ip)
                valid = False
            else:
                led_ips.add(led_ip)

            if led_name in led_names:
                repeated_names.add(led_name)
                valid = False
            else:
                led_names.add(led_name)

        if len(repeated_names) != 0:
            raise Exception(f"Field leds has the following names repeated: {repeated_names}")
        if len(repeated_ips) != 0:
            raise Exception(f"Field leds has the following ips repeated: {repeated_ips}")

        return valid


    def check_config_listeners_field(self, config_data_listeners:dict):

        MANDATORY_FIELDS = ["id", "type"]

        valid = True
        names, ids, repeated_names, repeated_ids = set(), set(), set(), set()

        for name, listener_config in config_data_listeners.items():

            # check if all mandatory fields exist
            missing_fields = MANDATORY_FIELDS.copy()
            for field in MANDATORY_FIELDS:
                if field in listener_config.keys():
                    missing_fields.remove(field)
            if len(missing_fields) != 0:
                valid = False
                raise Exception(f"Fields {missing_fields} are missing")

            id = listener_config["id"]

            if name in names:
                repeated_names.add(name)
                valid = False
            else:
                names.add(name)

            if id in ids:
                repeated_ids.add(id)
                valid = False
            else:
                ids.add(id)

        if len(repeated_names) != 0:
            raise Exception(f"Field listeners has the following names repeated: {repeated_names}")
        if len(repeated_ids) != 0:
            raise Exception(f"Field listeners has the following ips repeated: {repeated_ids}")

        return valid

    def check_config_listeners_led_map(self, config_data:dict):

        valid = True
        wrong_led, wrong_listener = set(), set()
        for map_dict in config_data["listener_led_map"]:
            if map_dict["led"] not in config_data["leds"].keys():
                valid = False
                wrong_led.add(map_dict["led"])
            if map_dict["listener"] not in config_data["listeners"].keys():
                valid = False
                wrong_listener.add(map_dict["listener"])

        if len(wrong_led) != 0:
            raise Exception(f"The following leds are not present in config file: ids {wrong_led}")
        if len(wrong_listener) != 0:
            raise Exception(f"The following listeners are not present in config file: ids {wrong_listener}")

        return valid