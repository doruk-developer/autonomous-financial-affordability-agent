import os
import pandas as pd

data_dir = "dataset"
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))
options_df = pd.read_csv(os.path.join(data_dir, "request_payment_options.csv"))

# 1. Inspect all events for User 22 in December 2024
u22_dec = events_df[(events_df["user_id"] == "user_22") & (events_df["event_date"].str.startswith("2024-12"))]
print("=== USER 22 ALL EVENTS IN DECEMBER 2024 ===")
cols = ["event_id", "description", "category", "amount", "event_date", "settlement_date", "status", "flexibility"]
print(u22_dec[cols].to_string())

# 2. Inspect payment options for request_22
print("\n=== PAYMENT OPTIONS FOR REQUEST_22 ===")
r22_opts = options_df[options_df["request_id"] == "request_22"]
print(r22_opts.to_string())