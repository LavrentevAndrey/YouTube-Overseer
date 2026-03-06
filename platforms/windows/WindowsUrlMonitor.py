from interfaces.IUrlMonitor import IUrlMonitor
from typing import Optional
import logging
import time

logger = logging.getLogger("WindowsUrlMonitor")

class WindowsUrlMonitor(IUrlMonitor):
    """
    Windows implementation of IUrlMonitor using uiautomation.
    """
    
    def __init__(self):
        try:
            import uiautomation as auto
            self.auto = auto
        except ImportError:
            logger.error("Failed to import uiautomation for Windows URL Monitor. Ensure it is installed.")
            self.auto = None

    def get_active_url(self) -> Optional[str]:
        """
        Returns the currently active URL if a browser is focused.
        """
        if not self.auto:
            return None
            
        try:
            # Walk the UI tree to find the focused browser and grab the address bar text
            # This is a naive MVP approach
            window = self.auto.GetForegroundWindow()
            if window and ("Chrome" in window.Name or "Edge" in window.Name or "Firefox" in window.Name):
                # Search for the address bar control
                addr_bar = window.EditControl(AutomationId="OmniboxViewViews") # Chrome ID
                if not addr_bar.Exists(0, 0):
                    addr_bar = window.EditControl(Name="Address and search bar") # Edge ID
                
                if addr_bar.Exists(0, 0):
                    return addr_bar.GetValuePattern().Value
            return None
                
        except Exception as e:
            logger.debug(f"Failed to get URL: {e}")
            return None

    def get_active_window_title(self) -> str:
        """
        Returns the title of the currently active window.
        """
        if not self.auto:
            return ""
            
        try:
            window = self.auto.GetForegroundWindow()
            if window:
                return window.Name
            return ""
        except Exception as e:
            logger.debug(f"Failed to get window title: {e}")
            return ""
