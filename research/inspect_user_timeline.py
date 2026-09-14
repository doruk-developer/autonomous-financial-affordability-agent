import os
import pandas as pd

events_df = pd.read_csv(os.path.join("dataset", "financial_events.csv"))

# Inspect all events for user_21 (around their request date 2026-04-03)
u21_events = events_df[events_df["user_id"] == "user_21"].copy()
print(f"Total events for user_21: {len(u21_events)}")
print("\nUnique event_types for user_21:")
print(u21_events["event_type"].value_counts())

print("\nRecent and future events for user_21:")
cols = ["event_id", "event_type", "description", "direction", "amount", "event_date", "settlement_date", "status", "flexibility", "minimum_allowed_amount"]
print(u21_events[cols].tail(15).to_string())

# Also check messages for user_21
msgs_df = pd.read_csv(os.path.join("dataset", "messages.csv"))
u21_msgs = msgs_df[msgs_df["user_id"] == "user_21"]
print(f"\nMessages for user_21 ({len(u21_msgs)}):")
for _, m in u21_msgs.iterrows():
    print(f"  [{m['sent_at']}] Event: {m['related_event_id']} | Text: {m['message_text']}")