from interfaces.INotificationProvider import INotificationProvider
import logging

logger = logging.getLogger("WindowsNotificationProvider")

class WindowsNotificationProvider(INotificationProvider):
    """
    Windows implementation of INotificationProvider using win10toast or ctypes.
    """
    
    def __init__(self):
        try:
            from win10toast import ToastNotifier
            self.toaster = ToastNotifier()
        except ImportError:
            logger.warning("win10toast not installed, falling back to ctypes MessageBox for notifications.")
            self.toaster = None
            import ctypes
            self.ctypes = ctypes

    def notify(self, title: str, message: str, **kwargs) -> bool:
        """
        Sends a desktop notification to the user.
        """
        try:
            display_timeout = kwargs.get("display_timeout", 5000)
            duration_secs = max(1, display_timeout // 1000)
            
            if self.toaster:
                self.toaster.show_toast(title, message, duration=duration_secs, threaded=True)
            else:
                # Windows MessageBox
                # 0x40 is MB_ICONINFORMATION
                self.ctypes.windll.user32.MessageBoxW(0, message, title, 0x40) # type: ignore
            return True
        except Exception as e:
            logger.error(f"Failed to send Windows notification: {e}")
            return False
