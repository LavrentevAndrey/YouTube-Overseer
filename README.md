# YouTube Overseer

YouTube Overseer is a Linux-native background service designed to manage productivity by tracking and limiting time spent on YouTube Shorts. It employs a 3-layer architecture to monitor active window titles, track usage time in a local database, and enforce daily limits by blocking network traffic to YouTube domains using iptables.

## Architecture

1.  **Interfaces (Layer 1)**: Abstract definitions for monitoring, blocking, and notifications, ensuring platform agility.
2.  **Core Engine (Layer 2)**: The central logic that tracks usage time, persists state in a SQLite database, and decides when to trigger enforcement.
3.  **Platform Execution (Layer 3)**: Linux-specific implementations using `xdotool` for window inspection and `iptables` for network blocking.

## Prerequisites

-   Linux OS (X11 or XWayland supported)
-   Python 3.8+
-   `xdotool` (for window monitoring)
-   `iptables` (for network blocking)
-   `sudo` privileges (for applying network rules)

## Installation

1.  Clone the repository.
2.  Ensure dependencies are installed:
    ```bash
    sudo apt install xdotool iptables
    ```
    (Or equivalent for your distribution)

## Usage

### Starting the Service

To run the overseer as a background user service:

```bash
python3 execution/setup_service.py
```

This script will:
1.  Generate a systemd user service file.
2.  Inject necessary environment variables (`DISPLAY`, `XAUTHORITY`).
3.  Enable and start the service automatically.

To run manually for debugging:

```bash
python3 main.py
```

### Checking Your Budget

To see your current daily usage and remaining time:

```bash
python3 execution/check_budget.py
```

### Emergency Stop

If you need to immediately unblock YouTube access (e.g., for work) or if the service misbehaves, run the killswitch script with root privileges:

```bash
sudo execution/cleanup_iptables.sh
```

## Configuration

The default daily limit is set to **30 minutes**. You can modify this in `core/BudgetEngine.py`:

```python
DAILY_LIMIT_SECONDS = 1800
```
