import os
import pandas as pd

data_dir = "dataset"
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))
samples_df = pd.read_csv(os.path.join(data_dir, "sample_requests.csv"))
messages_df = pd.read_csv(os.path.join(data_dir, "messages.csv"))

test_reqs = ["request_06", "request_15", "request_21", "request_22"]

for req_id in test_reqs:
    sample = samples_df[samples_df["request_id"] == req_id].iloc[0]
    u_id = sample["user_id"]
    req_date = sample["request_date"]
    safe_gt = sample["amount_safe_to_pay"]
    
    print("=" * 80)
    print(f"[{req_id}] User: {u_id} | Request Date: {req_date} | GT Safe Today: {safe_gt}")
    
    # Check messages
    u_msgs = messages_df[messages_df["user_id"] == u_id]
    if len(u_msgs) > 0:
        print(f"  Messages ({len(u_msgs)}):")
        for _, m in u_msgs.iterrows():
            print(f"    - [{m['sent_at']}] RelEvent: {m['related_event_id']} | {m['message_text']}")
    else:
        print("  Messages: None")
        
    # Check future or pending events (settlement_date >= req_date or status == pending)
    u_ev = events_df[events_df["user_id"] == u_id]
    future_ev = u_ev[(u_ev["settlement_date"] >= req_date) | (u_ev["event_date"] >= req_date) | (u_ev["status"].isin(["pending", "scheduled"]))]
    print(f"  Explicit Future/Pending Events ({len(future_ev)}):")
    cols = ["event_id", "event_type", "description", "direction", "amount", "event_date", "settlement_date", "status", "flexibility"]
    if len(future_ev) > 0:
        print(future_ev[cols].to_string())
    else:
        print("    None found directly with date >= req_date")