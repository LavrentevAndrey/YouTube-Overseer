import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add project root to path
sys.path.append(os.getcwd())

from platforms.linux.LinuxNetworkBlocker import LinuxNetworkBlocker

class TestLinuxNetworkBlocker(unittest.TestCase):
    @patch('subprocess.check_output')
    @patch('subprocess.call')
    @patch('subprocess.check_call')
    def test_block_youtube(self, mock_check_call, mock_call, mock_check_output):
        # Mock resolve_yt_ips.py output
        mock_check_output.return_value = b'192.168.1.1\n192.168.1.2\n'
        
        # Mock successful sudo execution
        mock_check_call.return_value = 0
        
        # Mock iptables checks (return 1 to simulate "not found" so rules are added)
        # 1. check chain exists (0=success) -> let's say it exists
        # 2. check jump rule (1=fail) -> implies we need to add it
        # 3. check specific rule (1=fail) -> implies we need to add it
        mock_call.side_effect = [0, 1, 1, 1] 
        
        blocker = LinuxNetworkBlocker()
        success = blocker.block_target("youtube.com")
        
        print("\n[Test] Blocking YouTube...")
        self.assertTrue(success)
        
        # Verify jump rule was added
        # We expect calls to subprocess.check_call for 'sudo iptables -A OUTPUT ...'
        # Check if any call args contained these values
        found_jump = any('OUTPUT' in str(call) and '-j' in str(call) and 'OVERSEER_BLOCK' in str(call) 
                        for call in mock_check_call.call_args_list)
        self.assertTrue(found_jump, "Jump rule should be added")
        
        # Verify IP drop rules were added
        found_drop = any('192.168.1.1' in str(call) and 'DROP' in str(call) 
                        for call in mock_check_call.call_args_list)
        self.assertTrue(found_drop, "Drop rule for IP should be added")
        
        print("[PASS] Block logic verified.")

    @patch('subprocess.check_call')
    def test_unblock_youtube(self, mock_check_call):
        blocker = LinuxNetworkBlocker()
        success = blocker.unblock_target("youtube.com")
        
        print("\n[Test] Unblocking YouTube...")
        self.assertTrue(success)
        
        # Verify cleanup script was called
        found_cleanup = any('cleanup_iptables.sh' in str(call) 
                           for call in mock_check_call.call_args_list)
        self.assertTrue(found_cleanup, "Cleanup script should be called")
        
        print("[PASS] Unblock logic verified.")

if __name__ == '__main__':
    unittest.main()
