"""
Configuration hot reload utility.

- Watches config files for changes and reloads them.
- Emits events/callbacks on reload.
"""

import time
import threading
from typing import Callable

def watch_config(path: str, on_reload: Callable):
    """
    Watch a config file for changes and call on_reload when changed.
    """
    last_mtime = None
    def watcher():
        nonlocal last_mtime
        while True:
            try:
                mtime = os.path.getmtime(path)
                if last_mtime is None:
                    last_mtime = mtime
                elif mtime != last_mtime:
                    last_mtime = mtime
                    on_reload()
            except Exception:
                pass
            time.sleep(2)
    thread = threading.Thread(target=watcher, daemon=True)
    thread.start()
