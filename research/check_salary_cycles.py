import os
import pandas as pd

events_df = pd.read_csv(os.path.join("dataset", "financial_events.csv"))

# Check salary events for user_06, user_21, user_22
test_users = ["user_06", "user_21", "user_22"]
for u in test_users:
    u_salaries = events_df[(events_df["user_id"] == u) & (events_df["direction"] == "credit") & (events_df["event_type"].isin(["income", "salary"]) | events_df["category"].str.contains("salary|payroll", case=False, na=False))]
    print(f"=== SALARIES FOR {u} ===")
    cols = ["event_id", "description", "category", "amount", "event_date", "settlement_date", "status"]
    print(u_salaries[cols].tail(4).to_string())

# Also check exact recurring subscriptions for user_22
print("\n=== USER 22 RECURRING ITEMS ===")
u22_rec = events_df[(events_df["user_id"] == "user_22") & (events_df["direction"] == "debit") & (events_df["event_type"] == "subscription")]
print(u22_rec[["event_id", "description", "category", "amount", "event_date", "settlement_date"]].tail(10).to_string())