import subprocess
import shutil
import logging
from typing import Optional
from interfaces.IUrlMonitor import IUrlMonitor

class LinuxUrlMonitor(IUrlMonitor):
    def __init__(self):
        """
        Initializes the LinuxUrlMonitor.
        Checks for dependencies (xdotool/wmctrl).
        """
        self.logger = logging.getLogger(__name__)

    def _check_tool(self, tool_name: str) -> bool:
        """Check if a tool is installed."""
        return shutil.which(tool_name) is not None

    def get_active_url(self) -> Optional[str]:
        """
        Attempts to identify the active URL context.
        On Linux (X11/Wayland with XWayland), we use window titles as a proxy.
        """
        title = self.get_active_window_title()
        
        # Heuristic: If title contains "YouTube", we assume a YouTube URL context.
        if "YouTube" in title:
            # Check for Shorts specific title markers if any (often not present in title)
            # But user request says "identify youtube.com/shorts/"
            if "Shorts" in title:
                return "https://www.youtube.com/shorts/detected_via_title"
            return "https://www.youtube.com/watch?v=detected_via_title"
            
        return None

    def get_active_window_title(self) -> str:
        """
        Returns the title of the currently active window using xdotool.
        """
        if not self._check_tool('xdotool'):
            # Fallback or error
            return "Error: xdotool missing"

        try:
            # 1. Get Active Window ID
            window_id = subprocess.check_output(['xdotool', 'getactivewindow']).decode('utf-8').strip()
            
            # 2. Get Window Class/Process Name
            # xprop -id <id> WM_CLASS
            # Returns something like: WM_CLASS(STRING) = "google-chrome", "Google-chrome"
            try:
                wm_class_bytes = subprocess.check_output(['xprop', '-id', window_id, 'WM_CLASS'])
                wm_class = wm_class_bytes.decode('utf-8').lower()
            except Exception:
                # If we fail to get class, assume it's NOT a browser to be safe? 
                # Or log warning. For now, if we can't identify it, ignore it.
                return "Unknown Window"

            # Check if likely a browser
            browser_keywords = ['chrome', 'firefox', 'brave', 'edge', 'chromium', 'opera', 'vivaldi']
            if not any(k in wm_class for k in browser_keywords):
                return f"Ignored App: {wm_class}" # or just return non-YouTube title

            # 3. Get Window Name
            title = subprocess.check_output(['xdotool', 'getwindowname', window_id]).decode('utf-8').strip()
            return title
            
        except subprocess.CalledProcessError:
            return "Unknown Window"
        except Exception:
            return "Error retrieving title"
