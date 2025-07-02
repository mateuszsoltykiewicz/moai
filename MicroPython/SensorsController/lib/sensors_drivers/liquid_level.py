from machine import ADC, Pin

class LiquidLevelSensor:
    def __init__(self, pin):
        self.adc = ADC(Pin(pin))

    def read(self):
        return {"liquid_level": self.adc.read_u16()}
