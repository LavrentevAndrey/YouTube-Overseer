import sys
import os
import time

# Add project root to path
sys.path.append(os.getcwd())

from platforms.linux.LinuxUrlMonitor import LinuxUrlMonitor

def main():
    print("Initializing LinuxUrlMonitor...")
    monitor = LinuxUrlMonitor()
    
    print("\n--- Monitoring Active Window (Press Ctrl+C to stop) ---")
    try:
        while True:
            title = monitor.get_active_window_title()
            url_context = monitor.get_active_url()
            
            print(f"Title: {title}")
            if url_context:
                print(f" > Detected Context: {url_context}")
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
