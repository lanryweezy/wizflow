"""
Base class for all trigger plugins in WizFlow.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable

class TriggerPlugin(ABC):
    """
    Abstract base class for a trigger plugin.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the trigger, e.g., 'file'."""
        pass

    @abstractmethod
    def start(self, config: Dict[str, Any], on_trigger: Callable[[Dict[str, Any]], None]):
        """
        Starts the trigger. When the trigger condition is met, it should call the
        `on_trigger` callback with a dictionary of context data.

        For triggers that run continuously (like watching files or a schedule),
        this method should block or run in a background thread. For triggers
        that run once (like a manual trigger), it should call `on_trigger`
        and then return.
        """
        pass
