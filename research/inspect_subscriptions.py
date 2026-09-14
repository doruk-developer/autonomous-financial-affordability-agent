import os
import pandas as pd

events_df = pd.read_csv(os.path.join("dataset", "financial_events.csv"))

# Inspect subscriptions and flexible events for user_21
u21_subs = events_df[(events_df["user_id"] == "user_21") & (events_df["event_type"].isin(["subscription", "expense"])) & (events_df["flexibility"] != "fixed")].copy()
cols = ["event_id", "event_type", "description", "category", "amount", "event_date", "settlement_date", "status", "flexibility", "minimum_allowed_amount"]
print("=== FLEXIBLE / SUBSCRIPTION EVENTS FOR USER_21 ===")
print(u21_subs[cols].to_string())

# Check specifically event_1815 and event_1816
print("\n=== TARGET EVENTS (event_1815, event_1816) ===")
print(events_df[events_df["event_id"].isin(["event_1815", "event_1816"])][cols].to_string())