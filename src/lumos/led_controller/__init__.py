from lumos.led_controller.led_controller import LedController

led_controller = LedController()


def start_led_controller_web_service(config_file=None):
    led_controller.config(config_file)

    from lumos.led_controller.web_service import WebService

    web_service = WebService()
    web_service.start()
