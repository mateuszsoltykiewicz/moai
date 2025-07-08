from machine import Pin

class FlameSensor:
    def __init__(self, pin):
        self.pin = Pin(pin, Pin.IN)

    def read(self):
        return {"flame": bool(self.pin.value())}
