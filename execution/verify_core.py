import sys
import os
import unittest
import shutil
from unittest.mock import MagicMock, patch
import time

# Add project root to path
sys.path.append(os.getcwd())

from core.BudgetEngine import BudgetEngine
from core.Database import Database

class TestCoreEngine(unittest.TestCase):
    def setUp(self):
        # Use a temporary DB
        self.test_db = ".tmp/test_overseer.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
            
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_database_logic(self):
        print("\n[Test] Database Logic...")
        db = Database(self.test_db)
        
        # Initial usage should be 0
        self.assertEqual(db.get_usage(), 0)
        
        # Increment
        db.increment_usage(10)
        self.assertEqual(db.get_usage(), 10)
        
        # Increment again
        db.increment_usage(5)
        self.assertEqual(db.get_usage(), 15)
        
        print("[PASS] Database operations verified.")

    def test_engine_logic(self):
        print("\n[Test] Budget Engine Logic...")
        
        # Mock components
        mock_monitor = MagicMock()
        mock_blocker = MagicMock()
        mock_blocker.is_blocked.return_value = False
        mock_notifier = MagicMock()
        
        # 1. Simulate Shorts active
        mock_monitor.get_active_url.return_value = "https://www.youtube.com/shorts/xyz"
        
        # Initialize Engine with low limit for testing
        engine = BudgetEngine(mock_monitor, mock_blocker, mock_notifier, self.test_db)
        engine.DAILY_LIMIT_SECONDS = 2 # 2 seconds limit
        
        # Manually tick engine to simulate loop
        print("Ticking engine (1s)...")
        engine._tick() # usage -> 1
        self.assertEqual(engine.db.get_usage(), 1)
        mock_blocker.block_target.assert_not_called()
        
        print("Ticking engine (2s)...")
        engine._tick() # usage -> 2
        mock_blocker.block_target.assert_not_called()
        
        print("Ticking engine (3s) - Should Block...")
        engine._tick() # usage -> 3
        
        # Verify blocking triggered
        mock_blocker.block_target.assert_called_with("youtube.com")
        mock_notifier.notify.assert_called()
        
        print("[PASS] Budget Engine enforcement verified.")

if __name__ == "__main__":
    unittest.main()
