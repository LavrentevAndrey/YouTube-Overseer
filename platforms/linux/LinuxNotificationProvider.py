from interfaces.INotificationProvider import INotificationProvider

import subprocess
import logging

logger = logging.getLogger("LinuxNotificationProvider")

class LinuxNotificationProvider(INotificationProvider):
    def notify(self, title: str, message: str, **kwargs) -> bool:
        cmd = ["notify-send", title, message]
        
        urgency = kwargs.get("urgency")
        if urgency in ("low", "normal", "critical"):
            cmd.extend(["-u", urgency])
            
        display_timeout = kwargs.get("display_timeout")
        if isinstance(display_timeout, int):
            cmd.extend(["-t", str(display_timeout)])
            
        icon_path = kwargs.get("icon_path")
        if icon_path:
            cmd.extend(["-i", icon_path])
            
        try:
            # We don't capture output, just run it
            subprocess.run(cmd, check=True)
            return True
        except Exception as e:
            logger.error(f"Failed to send Linux notification via notify-send: {e}")
            return False
