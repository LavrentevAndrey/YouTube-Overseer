import sys
import os
import datetime

# Add project root to path
sys.path.append(os.getcwd())

try:
    from core.Database import Database
    from core.BudgetEngine import BudgetEngine
except ImportError:
    # If running from execution dir, adjust path
    sys.path.append(os.path.dirname(os.getcwd()))
    from core.Database import Database
    from core.BudgetEngine import BudgetEngine

def main():
    db = Database()
    usage_seconds = db.get_usage()
    limit_seconds = BudgetEngine.DAILY_LIMIT_SECONDS
    
    usage_min = usage_seconds / 60
    limit_min = limit_seconds / 60
    remaining_min = limit_min - usage_min
    
    print(f"\n--- YouTube Overseer Budget ---")
    print(f"Date: {datetime.date.today().isoformat()}")
    print(f"Used: {usage_min:.1f} minutes")
    print(f"Limit: {limit_min:.1f} minutes")
    
    if remaining_min > 0:
        print(f"Remaining: {remaining_min:.1f} minutes")
        print("Status: OK")
    else:
        print(f"Over Budget: {abs(remaining_min):.1f} minutes")
        print("Status: BLOCKED")
    print("-------------------------------")

if __name__ == "__main__":
    main()
