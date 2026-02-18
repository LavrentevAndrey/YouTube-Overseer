import time
import logging
import datetime
from threading import Thread, Event
from core.Database import Database
from interfaces.IUrlMonitor import IUrlMonitor
from interfaces.INetworkBlocker import INetworkBlocker
from interfaces.INotificationProvider import INotificationProvider

class BudgetEngine:
    # Default limit: 30 minutes (1800 seconds)
    DAILY_LIMIT_SECONDS = 1800 

    def __init__(self, 
                 monitor: IUrlMonitor, 
                 blocker: INetworkBlocker, 
                 notifier: INotificationProvider,
                 db_path: str = ".tmp/overseer.db"):
        self.monitor = monitor
        self.blocker = blocker
        self.notifier = notifier
        self.db = Database(db_path)
        self.logger = logging.getLogger(__name__)
        self._stop_event = Event()
        self._thread = None

    def start(self):
        """Starts the engine in a background thread."""
        if self._thread is not None and self._thread.is_alive():
            return
        
        self._stop_event.clear()
        self._thread = Thread(target=self._loop, daemon=True)
        self._thread.start()
        self.logger.info("BudgetEngine started.")

    def stop(self):
        """Stops the engine."""
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.logger.info("BudgetEngine stopped.")

    def _loop(self):
        while not self._stop_event.is_set():
            try:
                self._tick()
            except Exception as e:
                self.logger.error(f"Error in engine loop: {e}")
            
            time.sleep(1)

    def _tick(self):
        # 1. Check current usage
        today = datetime.date.today().isoformat()
        usage = self.db.get_usage(today)
        
        # 2. Check active context
        url_context = self.monitor.get_active_url()
        
        is_shorts = url_context and ("shorts" in url_context.lower() or "youtube" in url_context.lower()) # Aggressive count for now based on title
        
        # 3. Update usage
        if is_shorts:
            self.db.increment_usage(1, today)
            usage += 1
            self.logger.debug(f"Usage incremented: {usage}/{self.DAILY_LIMIT_SECONDS}")

        # 4. Enforce Policy
        if usage > self.DAILY_LIMIT_SECONDS:
            if not self.blocker.is_blocked("youtube.com"):
                self.logger.info("Daily limit reached. Blocking YouTube.")
                self.notifier.notify("Time's Up", "YouTube daily limit reached. Blocking access.")
                self.blocker.block_target("youtube.com")
        else:
            # Optional: Auto-unblock next day handled by manual reset or just stay blocked until restart? 
            # For now, if usage < limit (e.g. next day or manual reset), ensure unblocked
            # But checking is_blocked every second might be expensive if it shells out.
            # Optimization: Only check if we think we might be blocked.
            pass
