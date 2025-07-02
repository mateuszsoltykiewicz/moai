from machine import WDT

class Watchdog:
    def __init__(self, timeout_ms=8000):
        self.wdt = WDT(timeout=timeout_ms)

    def feed(self):
        self.wdt.feed()
