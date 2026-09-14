import os
import pandas as pd
from datetime import datetime

events_df = pd.read_csv(os.path.join("dataset", "financial_events.csv"))
profiles_df = pd.read_csv(os.path.join("dataset", "financial_profiles.csv")).set_index("user_id")

# Analyze user_21
prof = profiles_df.loc["user_21"]
start_bal = float(prof["current_available_balance"])
min_bal = float(prof["minimum_balance_to_keep"])
req_amount = 1574.4

print(f"User 21: Start Balance = {start_bal}, Min Balance To Keep = {min_bal}")
print(f"Theoretical Max Surplus = {start_bal - min_bal}")

# Check all events between 2026-04-01 and 2026-05-01
u21 = events_df[events_df["user_id"] == "user_21"].copy()
print("\nAll events with event_type or category for user_21 in 2026:")
u21_2026 = u21[u21["event_date"] >= "2026-01-01"]
print(u21_2026[["event_id", "event_type", "description", "amount", "event_date", "settlement_date", "status", "flexibility"]].to_string())