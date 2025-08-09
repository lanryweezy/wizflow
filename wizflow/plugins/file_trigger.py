"""
File Trigger Plugin for WizFlow
"""

import time
from typing import Dict, Any, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from .trigger_base import TriggerPlugin

class FileTriggerHandler(FileSystemEventHandler):
    """A handler for file system events."""
    def __init__(self, on_trigger: Callable[[Dict[str, Any]], None]):
        self.on_trigger = on_trigger

    def on_created(self, event):
        """Called when a file or directory is created."""
        if not event.is_directory:
            self.on_trigger({
                "event_type": "created",
                "src_path": event.src_path,
            })

class FileTriggerPlugin(TriggerPlugin):
    """
    A trigger plugin that watches for file system events.
    """

    def __init__(self):
        self.observer = None

    @property
    def name(self) -> str:
        return "file"

    def start(self, config: Dict[str, Any], on_trigger: Callable[[Dict[str, Any]], None]):
        """Starts the file system watcher."""
        path = config.get("path", ".")

        event_handler = FileTriggerHandler(on_trigger)
        self.observer = Observer()
        self.observer.schedule(event_handler, path, recursive=True)
        self.observer.start()

        # In a real application, the main thread would block here, e.g., with a loop.
        # For testing and integration, we let the caller manage the lifetime.

    def stop(self):
        """Stops the file system watcher."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
