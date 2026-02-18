from abc import ABC, abstractmethod

class INotificationProvider(ABC):
    """
    Interface for forcing user notifications.
    """

    @abstractmethod
    def notify(self, title: str, message: str) -> bool:
        """
        Sends a notification to the user.
        Returns True if successful, False otherwise.
        """
        pass
