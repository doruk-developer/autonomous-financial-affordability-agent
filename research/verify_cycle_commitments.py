import os
import pandas as pd
from datetime import datetime

data_dir = "dataset"
profiles_df = pd.read_csv(os.path.join(data_dir, "financial_profiles.csv")).set_index("user_id")
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))
samples_df = pd.read_csv(os.path.join(data_dir, "sample_requests.csv"))

mismatch_ids = ["request_03", "request_04", "request_05", "request_06", "request_11", "request_13", "request_14", "request_19", "request_20", "request_21"]

print(f"{'REQ_ID':<12} | {'SURPLUS':<12} | {'GT_SAFE':<12} | {'COMMITTED':<12} | {'CALC_COMMIT'}")
print("-" * 75)

for req_id in mismatch_ids:
    row = samples_df[samples_df["request_id"] == req_id].iloc[0]
    u_id = row["user_id"]
    req_date = row["request_date"]
    req_dt = datetime.strptime(req_date, "%Y-%m-%d")
    gt_safe = float(row["amount_safe_to_pay"])
    
    prof = profiles_df.loc[u_id]
    start_bal = float(prof["current_available_balance"])
    min_bal = float(prof["minimum_balance_to_keep"])
    surplus = max(0.0, start_bal - min_bal)
    committed = surplus - gt_safe
    
    # Check pending debits
    u_ev = events_df[events_df["user_id"] == u_id]
    pend = u_ev[(u_ev["status"] == "pending") & (u_ev["direction"] == "debit")]["amount"].sum()
    
    # Calculate regular debits occurring between req_day and day 15 in past months
    req_day = req_dt.day
    u_past = u_ev[(u_ev["direction"] == "debit") & (u_ev["status"] == "settled")].copy()
    u_past["day"] = pd.to_datetime(u_past["event_date"]).dt.day
    u_past["month"] = u_past["event_date"].str.slice(0, 7)
    
    # Spend between req_day and day 15 in last full month
    months = sorted(u_past["month"].unique())
    last_mo = months[-2] if len(months) >= 2 else months[-1]
    mid_month_spend = u_past[(u_past["month"] == last_mo) & (u_past["day"] >= req_day) & (u_past["day"] <= 15)]["amount"].sum()
    
    total_calc = pend + mid_month_spend
    print(f"{req_id:<12} | {surplus:<12.1f} | {gt_safe:<12.1f} | {committed:<12.1f} | {total_calc:<12.1f}")