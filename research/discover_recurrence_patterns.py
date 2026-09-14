import os
import pandas as pd

data_dir = "dataset"
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))

# Inspect recent history of user_22 (before request date 2024-12-05)
u22 = events_df[events_df["user_id"] == "user_22"].copy()
print(f"=== USER 22 RECENT HISTORY ({len(u22)} total events) ===")
cols = ["event_id", "event_type", "description", "category", "amount", "event_date", "settlement_date", "status", "flexibility"]
recent_u22 = u22[u22["event_date"] >= "2024-10-01"]
print(recent_u22[cols].to_string())

# Also inspect user_06 recent history (before request date 2026-01-03)
u06 = events_df[events_df["user_id"] == "user_06"].copy()
print(f"\n=== USER 06 RECENT HISTORY ({len(u06)} total events) ===")
recent_u06 = u06[u06["event_date"] >= "2025-11-01"]
print(recent_u06[cols].to_string())