from src.lumos.LedController.LedController import LedController
led_controller = LedController()



def start_led_controller_web_service(config_file=None):

    led_controller.config(config_file)

    from src.lumos.LedController.WebService import WebService
    web_service = WebService()
    web_service.start()
