# /Python/libraries/modular/notification_replay/__init__.py
class NotificationReplayBuffer:
    def __init__(self, retention=100):
        self.buffer = []
        self.retention = retention

    def add(self, notification):
        self.buffer.append(notification)
        if len(self.buffer) > self.retention:
            self.buffer.pop(0)

    def replay(self, since_version):
        return [n for n in self.buffer if n['version'] > since_version]
