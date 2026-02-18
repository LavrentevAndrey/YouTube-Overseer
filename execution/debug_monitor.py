import sys
import os
import time
import logging

# Add project root to path
sys.path.append(os.getcwd())

from platforms.linux.LinuxUrlMonitor import LinuxUrlMonitor

def debug_monitor():
    monitor = LinuxUrlMonitor()
    print("--- Debugging LinuxUrlMonitor ---")
    print("Press Ctrl+C to stop.")
    
    while True:
        try:
            title = monitor.get_active_window_title()
            url_context = monitor.get_active_url()
            
            print(f"Title: '{title}'")
            print(f"Detected Context: '{url_context}'")
            print("-" * 20)
            
            time.sleep(1)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    debug_monitor()
