import subprocess
import logging
import sys
import os
import time
from typing import List
from interfaces.INetworkBlocker import INetworkBlocker

class LinuxNetworkBlocker(INetworkBlocker):
    CHAIN_NAME = "OVERSEER_BLOCK"

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._is_blocked_cache = False
        self._last_check_time = 0
        self._cache_ttl = 30  # seconds

    def _run_sudo_command(self, cmd: List[str]) -> bool:
        """Runs a command with sudo privileges."""
        try:
            full_cmd = ['sudo', '-n'] + cmd
            # We use check_call which waits for the command to complete.
            # Using stdout=DEVNULL to avoid spamming the console
            subprocess.check_call(full_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Sudo command '{cmd[0]}' failed. Your user requires NOPASSWD in visudo or the background process will fail.")
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
        subprocess.call(['sudo', '-n', 'iptables', '-N', self.CHAIN_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 3. Ensure Jump Rule
        # Check if exists: sudo iptables -C OUTPUT -j OVERSEER_BLOCK
        if subprocess.call(['sudo', '-n', 'iptables', '-C', 'OUTPUT', '-j', self.CHAIN_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            if not self._run_sudo_command(['iptables', '-A', 'OUTPUT', '-j', self.CHAIN_NAME]):
                # If we cannot even add the jump rule, stop early and throttle
                time.sleep(10)
                return False

        # 4. Add Rules
        current_rules = ""
        try:
            current_rules = subprocess.check_output(['sudo', '-n', 'iptables', '-S', self.CHAIN_NAME], stderr=subprocess.DEVNULL).decode('utf-8')
        except subprocess.CalledProcessError:
            # Check if sudo auth is failing
            if subprocess.call(['sudo', '-n', 'true'], stderr=subprocess.DEVNULL) != 0:
                self.logger.error("sudo requires password. Cannot enforce blocks. Please configure NOPASSWD.")
                time.sleep(10) # 10s cooldown to prevent tight loop from spamming logs
                return False

        print(f"Blocking {len(ips)} IPs...")
        success_count = 0
        for ip in ips:
            # Check if rule exists in the cached output to avoid running sudo for each IP
            if f"-d {ip}/32" not in current_rules and f"-d {ip} " not in current_rules:
                if self._run_sudo_command(['iptables', '-A', self.CHAIN_NAME, '-d', ip, '-j', 'DROP']):
                    success_count += 1
        
        print(f"Blocked {success_count} new IPs.")
        
        if success_count > 0 or len(ips) > 0:
            self._is_blocked_cache = True
            self._last_check_time = time.time()
            return True
        return False

    def unblock_target(self, target: str) -> bool:
        """
        Unblocks network traffic by calling the cleanup script.
        """
        script_path = os.path.join("execution", "cleanup_iptables.sh")
        if not os.path.exists(script_path):
             script_path = os.path.abspath("execution/cleanup_iptables.sh")

        print("Lifting network blocks...")
        success = self._run_sudo_command(['bash', script_path])
        if success:
            self._is_blocked_cache = False
            self._last_check_time = time.time()
        return success

    def is_blocked(self, target: str) -> bool:
        """
        Checks if the custom chain has rules.
        Uses caching to avoid spanning PAM and system processes.
        """
        now = time.time()
        if now - self._last_check_time < self._cache_ttl:
            return self._is_blocked_cache

        try:
            # Check if chain has any rules
            output = subprocess.check_output(['sudo', '-n', 'iptables', '-L', self.CHAIN_NAME, '-n'], stderr=subprocess.DEVNULL)
            is_blocked = b"DROP" in output
            self._is_blocked_cache = is_blocked
            self._last_check_time = now
            return is_blocked
        except subprocess.CalledProcessError:
            # The chain doesn't exist, or sudo auth failed
            self._is_blocked_cache = False
            self._last_check_time = now
            return False
