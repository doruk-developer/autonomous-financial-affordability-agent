import os
import pandas as pd

data_dir = "dataset"
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))

# Inspect events for user_22 between day 5 and day 15 of every month
u22 = events_df[(events_df["user_id"] == "user_22") & (events_df["direction"] == "debit")].copy()
u22["day"] = pd.to_datetime(u22["event_date"]).dt.day
u22_window = u22[(u22["day"] >= 5) & (u22["day"] <= 15)]

print("=== USER 22 EXPENSES BETWEEN DAY 5 AND DAY 15 ACROSS MONTHS ===")
cols = ["event_date", "description", "category", "amount", "status", "flexibility"]
print(u22_window[cols].sort_values("event_date").tail(20).to_string())