import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

try:
    from interfaces.IUrlMonitor import IUrlMonitor
    from interfaces.INetworkBlocker import INetworkBlocker
    from interfaces.INotificationProvider import INotificationProvider
    from platforms.linux.LinuxUrlMonitor import LinuxUrlMonitor
    from platforms.linux.LinuxNetworkBlocker import LinuxNetworkBlocker
    from platforms.linux.LinuxNotificationProvider import LinuxNotificationProvider

    print("Successfully imported all interfaces and Linux implementations.")

    # Instantiate Linux classes to ensure they match the interface (even if methods are empty/TODO)
    monitor = LinuxUrlMonitor()
    blocker = LinuxNetworkBlocker()
    notifier = LinuxNotificationProvider()

    print("Successfully instantiated Linux implementations.")

except Exception as e:
    print(f"Verification failed: {e}")
    sys.exit(1)
