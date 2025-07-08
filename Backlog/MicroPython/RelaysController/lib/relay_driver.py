from machine import Pin

class RelayDriver:
    def __init__(self, relay_pins, default_state=None):
        self.relays = [Pin(pin, Pin.OUT) for pin in relay_pins]
        self.safe_state()
        if default_state:
            self.set_all(default_state)

    def set(self, idx, value):
        if 0 <= idx < len(self.relays):
            self.relays[idx].value(value)

    def set_all(self, states):
        for i, val in enumerate(states):
            self.set(i, val)

    def safe_state(self):
        self.set_all([0] * len(self.relays))

    def handle_command(self, cmd, command_map):
        # Expecting a string command, e.g., "ON_1"
        idx = command_map.get(cmd)
        if idx is not None:
            relay_idx = idx // 2
            state = 1 if "ON" in cmd else 0
            self.set(relay_idx, state)
            return b"OK"
        return b"ERR"
