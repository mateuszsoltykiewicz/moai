from machine import Pin
import dht

class DHT11:
    def __init__(self, pin):
        self.sensor = dht.DHT11(Pin(pin))

    def read(self):
        try:
            self.sensor.measure()
            return {
                "temperature": self.sensor.temperature(),
                "humidity": self.sensor.humidity()
            }
        except Exception as e:
            return {"error": str(e)}
