# Directive: Linux URL Monitoring (MVP)

## Overview
This directive outlines the standard procedure for detecting active URLs (or their proxies, i.e., Window Titles) on Linux systems using `wmctrl` and `xdotool`.

## Prerequisites
*   **X11**: `wmctrl` and `xdotool` are required.
*   **Wayland**: (Future) `wtype` or compositor-specific tools.
*   **Browsers**: Google Chrome, Firefox, Brave.

## Strategy: Title Inspection

Since direct URL access fails without accessibility tools (AT-SPI) or browser extensions, we rely on **Window Title Inspection** as a proxy.

1.  **Identify Active Window**:
    *   Use `xdotool getactivewindow` to get the Window ID.

2.  **Get Window Title**:
    *   Use `xdotool getwindowname <WINDOW_ID>`.
    *   Alternatively, parse `wmctrl -lp` output.

3.  **Heuristics for YouTube Shorts**:
    *   **YouTube Detection**: Check if title contains "YouTube".
    *   **Shorts Detection**:
        *   Window titles often do not contain "shorts".
        *   *Protocol*: If title contains "YouTube", we treat it as potential YouTube usage. 
        *   *Future*: Inspect browser specific files (e.g., sessionstore) if more granularity is needed.

## Implementation Details (Python)

```python
import subprocess
import shutil

def get_active_window_title_linux():
    # Check if tools are installed
    if not shutil.which('xdotool'):
        return None
        
    try:
        # Get active window ID
        id_bytes = subprocess.check_output(['xdotool', 'getactivewindow'])
        window_id = id_bytes.decode('utf-8').strip()
        
        # Get window title
        title_bytes = subprocess.check_output(['xdotool', 'getwindowname', window_id])
        return title_bytes.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        return None
```