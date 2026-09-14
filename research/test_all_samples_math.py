import os
import pandas as pd
from datetime import datetime

data_dir = "dataset"
profiles_df = pd.read_csv(os.path.join(data_dir, "financial_profiles.csv")).set_index("user_id")
samples_df = pd.read_csv(os.path.join(data_dir, "sample_requests.csv"))
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))

print(f"{'REQ_ID':<12} | {'USER':<9} | {'REQ_AMT':<10} | {'START_BAL':<10} | {'MIN_BAL':<10} | {'MAX_SURPLUS':<11} | {'SAFE_TODAY':<10} | {'DIFF (COMMITTED)':<16} | {'STATUS':<20}")
print("-" * 125)

for idx, row in samples_df.iterrows():
    req_id = row["request_id"]
    user_id = row["user_id"]
    req_amt = float(row["requested_amount"])
    prof = profiles_df.loc[user_id]
    start_bal = float(prof["current_available_balance"])
    min_bal = float(prof["minimum_balance_to_keep"])
    surplus = max(0.0, start_bal - min_bal)
    safe_today = float(row["amount_safe_to_pay"])
    diff = surplus - safe_today
    status = row["affordability_status"]
    
    print(f"{req_id:<12} | {user_id:<9} | {req_amt:<10.1f} | {start_bal:<10.1f} | {min_bal:<10.1f} | {surplus:<11.1f} | {safe_today:<10.1f} | {diff:<16.1f} | {status:<20}")