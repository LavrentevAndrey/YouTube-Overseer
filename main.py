import sys
import os
import time
import logging
import signal
from core.BudgetEngine import BudgetEngine

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("overseer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Main")

def main():
    logger.info("Starting YouTube Overseer...")
    
    # 1. Platform Detection (Simplified for Linux MVP)
    if sys.platform != "linux":
        logger.error("Only Linux is supported in this MVP.")
        sys.exit(1)

    try:
        from platforms.linux.LinuxUrlMonitor import LinuxUrlMonitor
        from platforms.linux.LinuxNetworkBlocker import LinuxNetworkBlocker
        from platforms.linux.LinuxNotificationProvider import LinuxNotificationProvider
    except ImportError as e:
        logger.critical(f"Failed to import platform modules: {e}")
        sys.exit(1)

    # 2. Instantiate Components
    monitor = LinuxUrlMonitor()
    blocker = LinuxNetworkBlocker()
    notifier = LinuxNotificationProvider()

    # 3. Instantiate Engine
    engine = BudgetEngine(monitor, blocker, notifier)
    
    # 4. Handle Signals
    def signal_handler(sig, frame):
        logger.info("Shutdown signal received.")
        engine.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 5. Start Engine
    engine.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop()

if __name__ == "__main__":
    main()
