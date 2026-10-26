class ActuatorController:
    def __init__(self, gpio_cfg):
        self.gpio_cfg = gpio_cfg
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            for pin in self.gpio_cfg.values():
                self.GPIO.setup(pin, self.GPIO.OUT)
                self.GPIO.output(pin, self.GPIO.LOW)
            self.mock = False
        except ImportError:
            self.mock = True

    def trigger(self, action):
        if self.mock:
            print(f"Mock actuator: {action}")
        else:
            pin = self.gpio_cfg.get(action)
            if pin:
                self.GPIO.output(pin, self.GPIO.HIGH)
                
    def cleanup(self):
        if not self.mock:
            self.GPIO.cleanup()