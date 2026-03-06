from abc import ABC, abstractmethod

class INotificationProvider(ABC):
    """
    Interface for forcing user notifications.
    """

    @abstractmethod
    def notify(self, title: str, message: str, **kwargs) -> bool:
        """
        Sends a notification to the user.
        Optional kwargs:
        - urgency: str ('low', 'normal', 'critical')
        - display_timeout: int (milliseconds to stay on screen)
        - icon_path: str (path to an icon)
        Returns True if successful, False otherwise.
        """
        pass
