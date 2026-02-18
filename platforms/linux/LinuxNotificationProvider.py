from interfaces.INotificationProvider import INotificationProvider

class LinuxNotificationProvider(INotificationProvider):
    def notify(self, title: str, message: str) -> bool:
        # TODO: Implement Linux notifications (e.g., via notify-send or dbus)
        print(f"Notification: {title} - {message}")
        return True
