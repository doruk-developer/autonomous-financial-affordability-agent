import os
import json
import pandas as pd
from datetime import datetime, timedelta

data_dir = "dataset"
profiles_df = pd.read_csv(os.path.join(data_dir, "financial_profiles.csv")).set_index("user_id")
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))
rates_df = pd.read_csv(os.path.join(data_dir, "exchange_rates.csv"))
samples_df = pd.read_csv(os.path.join(data_dir, "sample_requests.csv"))

# Load extracted image amounts
with open(os.path.join(data_dir, "extracted_image_amounts.json"), "r") as f:
    extracted_images = json.load(f)

for event_id, item in extracted_images.items():
    mask = events_df["event_id"] == event_id
    events_df.loc[mask, "amount"] = item["amount"]
    if "currency" in item:
        events_df.loc[mask, "currency"] = item["currency"]

# Convert event dates
events_df["event_dt"] = pd.to_datetime(events_df["event_date"])
events_df["settle_dt"] = pd.to_datetime(events_df["settlement_date"])

print("=== RUNNING BASELINE ENGINE SIMULATION ON 25 SAMPLES ===\n")
print(f"{'REQ_ID':<12} | {'GT_SAFE':<10} | {'PRED_SAFE':<10} | {'MATCH?':<8} | {'GT_STATUS':<20}")
print("-" * 75)

matches = 0
for idx, row in samples_df.iterrows():
    req_id = row["request_id"]
    user_id = row["user_id"]
    req_dt = pd.to_datetime(row["request_date"])
    req_amt = float(row["requested_amount"])
    gt_safe = float(row["amount_safe_to_pay"])
    
    prof = profiles_df.loc[user_id]
    start_bal = float(prof["current_available_balance"])
    min_bal = float(prof["minimum_balance_to_keep"])
    
    # Simple direct surplus baseline
    simple_surplus = max(0.0, start_bal - min_bal)
    
    # Check pending debits
    u_events = events_df[events_df["user_id"] == user_id]
    pending_debits = u_events[(u_events["status"] == "pending") & (u_events["direction"] == "debit")]["amount"].sum()
    
    pred_safe = min(req_amt, max(0.0, simple_surplus - pending_debits))
    
    # Check if exact or close
    is_match = abs(pred_safe - gt_safe) < 1.0
    if is_match:
        matches += 1
    
    match_str = "YES" if is_match else f"DIFF:{pred_safe - gt_safe:.1f}"
    print(f"{req_id:<12} | {gt_safe:<10.1f} | {pred_safe:<10.1f} | {match_str:<8} | {row['affordability_status']:<20}")

print("-" * 75)
print(f"Direct Baseline Match: {matches} / 25 cases")