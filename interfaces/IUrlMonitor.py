from abc import ABC, abstractmethod
from typing import Optional

class IUrlMonitor(ABC):
    """
    Interface for monitoring active URLs.
    """

    @abstractmethod
    def get_active_url(self) -> Optional[str]:
        """
        Returns the currently active URL if a browser is focused.
        Returns None if no browser is focused or URL cannot be retrieved.
        """
        pass

    @abstractmethod
    def get_active_window_title(self) -> str:
        """
        Returns the title of the currently active window.
        Useful for context when URL is unavailable.
        """
        pass
