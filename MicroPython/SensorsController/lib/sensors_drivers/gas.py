from machine import Pin

class GasSensor:
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN)

    def read(self):
        return {"gas": bool(self.pin.value())}
