import os
import json
import pandas as pd
from datetime import datetime, timedelta

data_dir = "dataset"
profiles_df = pd.read_csv(os.path.join(data_dir, "financial_profiles.csv")).set_index("user_id")
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))
rates_df = pd.read_csv(os.path.join(data_dir, "exchange_rates.csv"))
samples_df = pd.read_csv(os.path.join(data_dir, "sample_requests.csv"))
messages_df = pd.read_csv(os.path.join(data_dir, "messages.csv"))

# Load extracted amounts
with open(os.path.join(data_dir, "extracted_image_amounts.json"), "r") as f:
    extracted_images = json.load(f)

# Fill missing amounts in events
for event_id, item in extracted_images.items():
    mask = events_df["event_id"] == event_id
    events_df.loc[mask, "amount"] = item["amount"]
    if "currency" in item:
        events_df.loc[mask, "currency"] = item["currency"]

print("=== CHECKING CASHFLOW ON FIRST 3 SAMPLE CASES ===\n")

for i in [0, 20, 22]: # request_01, request_21, request_23
    row = samples_df.iloc[i]
    req_id = row["request_id"]
    user_id = row["user_id"]
    req_date = datetime.strptime(row["request_date"], "%Y-%m-%d")
    end_date = req_date + timedelta(days=90)
    req_amount = float(row["requested_amount"])
    
    prof = profiles_df.loc[user_id]
    home_curr = prof["home_currency"]
    start_bal = float(prof["current_available_balance"])
    min_bal = float(prof["minimum_balance_to_keep"])
    
    print(f"[{req_id}] User: {user_id} | Home Currency: {home_curr}")
    print(f"  Start Balance: {start_bal} | Min Balance To Keep: {min_bal} | Requested: {req_amount}")
    print(f"  Ground Truth: Safe Today: {row['amount_safe_to_pay']} | Status: {row['affordability_status']}")
    print(f"  Ground Truth Earliest Full Date: {row['earliest_date_for_full_payment']}")
    print(f"  Ground Truth Explanation: {row['decision_explanation']}")
    
    # Filter user events within 90-day window
    user_events = events_df[events_df["user_id"] == user_id].copy()
    user_events["event_dt"] = pd.to_datetime(user_events["event_date"])
    
    # Check events in window
    win_events = user_events[(user_events["event_dt"] >= req_date) & (user_events["event_dt"] <= end_date)]
    print(f"  Events in 90-day window: {len(win_events)} (debits: {len(win_events[win_events['direction']=='debit'])}, credits: {len(win_events[win_events['direction']=='credit'])})")
    print("-" * 75)