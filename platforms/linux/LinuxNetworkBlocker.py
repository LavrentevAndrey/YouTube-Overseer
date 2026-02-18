import subprocess
import logging
import sys
import os
from typing import List
from interfaces.INetworkBlocker import INetworkBlocker

class LinuxNetworkBlocker(INetworkBlocker):
    CHAIN_NAME = "OVERSEER_BLOCK"

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def _run_sudo_command(self, cmd: List[str]) -> bool:
        """Runs a command with sudo privileges."""
        try:
            full_cmd = ['sudo'] + cmd
            # We use check_call which waits for the command to complete.
            # Only works if user has NOPASSWD or is interacting with terminal.
            subprocess.check_call(full_cmd)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e}")
            return False

    def block_target(self, target: str) -> bool:
        """
        Blocks network traffic to the specified target (YouTube).
        Resolves IPs and adds them to the custom iptables chain.
        """
        if target.lower() not in ["youtube", "youtube.com"]:
            self.logger.warning(f"Blocking target '{target}' not explicitly supported yet.")
            return False

        print(f"Resolving IPs for {target}...")
        # 1. Resolve IPs
        try:
            # Assumes execution dir is relative to CWD or in python path
            script_path = os.path.join("execution", "resolve_yt_ips.py")
            if not os.path.exists(script_path):
                 # Fallback for when running from project root
                 script_path = os.path.abspath("execution/resolve_yt_ips.py")
            
            # This script prints IPs to stdout
            result = subprocess.check_output([sys.executable, script_path])
            ips = result.decode('utf-8').strip().split('\n')
            ips = [ip.strip() for ip in ips if ip.strip()]
            
            if not ips:
                self.logger.error("No IPs resolved for blocking.")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to resolve IPs: {e}")
            return False

        # 2. Ensure Chain Exists
        # sudo iptables -N OVERSEER_BLOCK (might fail if exists, ignores error)
        subprocess.call(['sudo', 'iptables', '-N', self.CHAIN_NAME], stderr=subprocess.DEVNULL)

        # 3. Ensure Jump Rule
        # Check if exists: sudo iptables -C OUTPUT -j OVERSEER_BLOCK
        if subprocess.call(['sudo', 'iptables', '-C', 'OUTPUT', '-j', self.CHAIN_NAME], stderr=subprocess.DEVNULL) != 0:
            self._run_sudo_command(['iptables', '-A', 'OUTPUT', '-j', self.CHAIN_NAME])

        # 4. Add Rules
        print(f"Blocking {len(ips)} IPs...")
        success_count = 0
        for ip in ips:
            # Check if rule exists
            check_cmd = ['sudo', 'iptables', '-C', self.CHAIN_NAME, '-d', ip, '-j', 'DROP']
            if subprocess.call(check_cmd, stderr=subprocess.DEVNULL) != 0:
                if self._run_sudo_command(['iptables', '-A', self.CHAIN_NAME, '-d', ip, '-j', 'DROP']):
                    success_count += 1
        
        print(f"Blocked {success_count} new IPs.")
        return True

    def unblock_target(self, target: str) -> bool:
        """
        Unblocks network traffic by calling the cleanup script.
        """
        script_path = os.path.join("execution", "cleanup_iptables.sh")
        if not os.path.exists(script_path):
             script_path = os.path.abspath("execution/cleanup_iptables.sh")

        print("Lifting network blocks...")
        return self._run_sudo_command(['bash', script_path])

    def is_blocked(self, target: str) -> bool:
        """
        Checks if the custom chain has rules.
        """
        try:
            # Check if chain has any rules
            # iptables -L OVERSEER_BLOCK -n | grep DROP
            output = subprocess.check_output(['sudo', 'iptables', '-L', self.CHAIN_NAME, '-n'], stderr=subprocess.DEVNULL)
            return b"DROP" in output
        except subprocess.CalledProcessError:
            # Chain doesn't exist?
            return False
