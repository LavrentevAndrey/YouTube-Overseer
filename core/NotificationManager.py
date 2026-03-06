import time
import logging
from typing import Dict, Any, Optional
from interfaces.INotificationProvider import INotificationProvider

logger = logging.getLogger("NotificationManager")

class NotificationManager:
    """
    Orchestrates notifications with customizable timing, rate-limiting, and context formatting.
    """
    def __init__(self, provider: INotificationProvider):
        self.provider = provider
        self.last_notification_time = 0.0
        self._notified_timestamps = set()

    def process_context(self, context: Dict[str, Any]):
        """
        Receives context from the BudgetEngine and decides whether to send a notification.
        context example:
        {
            "time_remaining_secs": 300,
            "daily_limit_secs": 1800,
            "active_url": "youtube.com/shorts/...",
            "window_title": "YouTube - Mozilla Firefox"
        }
        """
        time_remaining = context.get("time_remaining_secs", 0)
        
        # 1. Custom Parsing Stub (Extensibility Feature)
        parsed_message = self.parse_context_for_message(context)
        
        # 2. Timing Strategy: Timestamps
        # Notify exactly at 15 mins (900s) and 5 mins (300s) left
        timestamps_to_notify = [900, 300]
        for ts in timestamps_to_notify:
            if ts >= time_remaining > ts - 5: # 5-second window
                if ts not in self._notified_timestamps:
                    self._notified_timestamps.add(ts)
                    self._send_alert(
                        title=f"{ts//60} Minutes Remaining",
                        message=parsed_message or "You have limited time remaining for YouTube.",
                        urgency="normal"
                    )
                    return

        # 3. Timing Strategy: Scaling Frequency
        # E.g. Under 5 mins: every 2 minutes. Under 1 min: every 30 seconds
        now = time.time()
        time_since_last = now - self.last_notification_time
        
        if time_remaining <= 60 and time_remaining > 0:
            if time_since_last >= 30:
                self._send_alert("Almost out of time!", parsed_message or f"{time_remaining} seconds left.", "critical")
        elif time_remaining <= 300 and time_remaining > 60:
            if time_since_last >= 120:
                self._send_alert("Time is running out", parsed_message or f"{time_remaining//60} minutes left.", "normal")

    def parse_context_for_message(self, context: Dict[str, Any]) -> Optional[str]:
        """
        STUB: In the future, this can be expanded to parse the window_title or active_url
        to extract the YouTube video name and format a custom message.
        """
        # title = context.get("window_title", "")
        # url = context.get("active_url", "")
        # Future Feature: Extract video name from title
        return None

    def notify_limit_reached(self):
        self._send_alert(
            title="Time's Up", 
            message="YouTube daily limit reached. Blocking access.", 
            urgency="critical",
            display_timeout=10000
        )

    def _send_alert(self, title: str, message: str, urgency: str = "normal", display_timeout: int = 5000):
        self.last_notification_time = time.time()
        self.provider.notify(title, message, urgency=urgency, display_timeout=display_timeout)
