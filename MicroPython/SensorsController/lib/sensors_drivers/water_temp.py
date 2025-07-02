from machine import ADC, Pin

class WaterTempSensor:
    def __init__(self, pin):
        self.adc = ADC(Pin(pin))

    def read(self):
        return {"water_temp_raw": self.adc.read_u16()}
