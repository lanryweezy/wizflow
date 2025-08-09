"""
Schedule Trigger Plugin for WizFlow
"""

import time
from typing import Dict, Any, Callable
from croniter import croniter

from .trigger_base import TriggerPlugin

class ScheduleTriggerPlugin(TriggerPlugin):
    """
    A trigger plugin that runs workflows on a schedule using cron expressions.
    """
    def __init__(self):
        self._stopped = False

    @property
    def name(self) -> str:
        return "schedule"

    def start(self, config: Dict[str, Any], on_trigger: Callable[[Dict[str, Any]], None]):
        """Starts the scheduler."""
        cron_expression = config.get("schedule")
        if not cron_expression:
            raise ValueError("Cron expression not provided for schedule trigger.")

        # In a real app, you'd want a more robust way to get the base time,
        # especially across restarts.
        base_time = time.time()

        while not self._stopped:
            try:
                iter = croniter(cron_expression, base_time)
                next_run_time = iter.get_next()

                sleep_seconds = max(0, next_run_time - time.time())

                # Sleep in small increments to be responsive to the stop flag
                sleep_end_time = time.time() + sleep_seconds
                while time.time() < sleep_end_time and not self._stopped:
                    time.sleep(0.1)

                if self._stopped:
                    break

                on_trigger({})
                base_time = time.time()
            except Exception as e:
                # Avoid crashing the trigger loop on error
                print(f"Error in schedule trigger: {e}")
                time.sleep(60) # Wait a minute before retrying

    def stop(self):
        """Stops the scheduler."""
        self._stopped = True
