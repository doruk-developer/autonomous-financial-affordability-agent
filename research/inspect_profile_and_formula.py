import os
import pandas as pd

data_dir = "dataset"
profiles_df = pd.read_csv(os.path.join(data_dir, "financial_profiles.csv")).set_index("user_id")
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))

u21_prof = profiles_df.loc["user_21"]
print("=== USER 21 PROFILE ===")
for col in profiles_df.columns:
    print(f"  {col}: {u21_prof[col]}")

# Look at all expenses between 2026-04-03 and 2026-04-15
u21_events = events_df[events_df["user_id"] == "user_21"]
print("\n=== UPCOMING OR SCHEDULED EVENTS FOR USER 21 (April 2026) ===")
apr_events = u21_events[(u21_events["event_date"] >= "2026-04-01") | (u21_events["settlement_date"] >= "2026-04-01")]
print(apr_events[["event_id", "event_type", "description", "category", "amount", "event_date", "settlement_date", "status", "flexibility"]].to_string())