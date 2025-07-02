from machine import SPI, Pin
import ujson
import time
from lib.config_manager import log_event

# Import your MCP2515 library (choose one and place it in your project)
from mcp2515 import MCP2515  # This should be the MicroPython MCP2515 driver you use

class CANBusHandler:
    def __init__(self, config):
        # SPI and MCP2515 setup
        spi_bus = config["canbus"]["spi_bus"]
        cs_pin = config["canbus"]["cs_pin"]
        int_pin = config["canbus"]["int_pin"]
        bitrate = config["canbus"]["bitrate"]
        self.can_id = config["canbus"]["address"]

        self.spi = SPI(spi_bus, baudrate=1000000, polarity=0, phase=0)
        self.cs = Pin(cs_pin, Pin.OUT)
        self.int_pin = Pin(int_pin, Pin.IN)
        self.mcp = MCP2515(self.spi, self.cs, self.int_pin)
        self.mcp.reset()
        self.mcp.setBitrate(bitrate)
        self.mcp.setNormalMode()

        self.streaming_enabled = config.get("streaming_enabled", False)
        self.last_stream_cmd = time.ticks_ms()

    def poll(self):
        # Check for incoming CAN messages
        if self.mcp.checkReceive():
            msg = self.mcp.readMessage()
            if msg is not None:
                try:
                    payload = ujson.loads(bytes(msg['data']).decode())
                    cmd = payload.get("cmd")
                    if cmd == "ENABLE_STREAM":
                        self.streaming_enabled = True
                        self.last_stream_cmd = time.ticks_ms()
                        log_event("CAN_CMD", "Streaming enabled")
                    elif cmd == "DISABLE_STREAM":
                        self.streaming_enabled = False
                        log_event("CAN_CMD", "Streaming disabled")
                    elif cmd == "CONFIG":
                        # Accept config updates via CAN if needed
                        # self.handle_config(payload)
                        pass
                except Exception as e:
                    log_event("CAN_PARSE_ERROR", str(e))
        # Optional: Watchdog for streaming timeout
        if self.streaming_enabled:
            if time.ticks_diff(time.ticks_ms(), self.last_stream_cmd) > 60000:  # 60s timeout
                self.streaming_enabled = False
                log_event("CAN_STREAM_TIMEOUT", "Streaming auto-disabled due to inactivity")

    def send_sensor_data(self, sensor_data):
        try:
            msg = ujson.dumps(sensor_data)
            # CAN: max 8 bytes per frame; split if needed
            msg_bytes = msg.encode()
            frames = [msg_bytes[i:i+8] for i in range(0, len(msg_bytes), 8)]
            for frame in frames:
                self.mcp.sendMessage(self.can_id, frame)
            log_event("CAN_SEND", msg)
        except Exception as e:
            log_event("CAN_SEND_ERROR", str(e))
