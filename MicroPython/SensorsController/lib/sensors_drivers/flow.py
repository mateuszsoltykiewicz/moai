from machine import Pin

class FlowSensor:
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN)

    def read(self):
        return {"flow": bool(self.pin.value())}
