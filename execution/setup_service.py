import os
import sys
import subprocess

SERVICE_TEMPLATE = """[Unit]
Description=YouTube Overseer Service
After=network.target graphical-session.target
Wants=graphical-session.target

[Service]
ExecStart={python_path} {script_path}
WorkingDirectory={working_dir}
Environment=DISPLAY={display}
Environment=XAUTHORITY={xauthority}
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
"""

def setup_service():
    print("Setting up systemd user service...")
    
    # Paths
    current_dir = os.getcwd()
    script_path = os.path.join(current_dir, "main.py")
    python_path = sys.executable
    
    # Environment Variables (Need explicit DISPLAY for GUI interaction)
    display = os.environ.get("DISPLAY", ":0")
    xauthority = os.environ.get("XAUTHORITY", os.path.expanduser("~/.Xauthority"))
    
    print(f"Using Environment: DISPLAY={display}, XAUTHORITY={xauthority}")

    # Service file content
    service_content = SERVICE_TEMPLATE.format(
        python_path=python_path,
        script_path=script_path,
        working_dir=current_dir,
        display=display,
        xauthority=xauthority
    )
    
    # Systemd user directory
    systemd_dir = os.path.expanduser("~/.config/systemd/user")
    if not os.path.exists(systemd_dir):
        os.makedirs(systemd_dir)
        
    service_file_path = os.path.join(systemd_dir, "youtube-overseer.service")
    
    # Write service file
    with open(service_file_path, "w") as f:
        f.write(service_content)
    
    print(f"Service file updated at: {service_file_path}")
    
    # Reload daemon
    subprocess.run(["systemctl", "--user", "daemon-reload"])
    
    # Enable and start
    subprocess.run(["systemctl", "--user", "enable", "youtube-overseer"])
    subprocess.run(["systemctl", "--user", "restart", "youtube-overseer"])
    
    print("Service restarted with new configuration.")
    print("Check status with: systemctl --user status youtube-overseer")

if __name__ == "__main__":
    setup_service()
