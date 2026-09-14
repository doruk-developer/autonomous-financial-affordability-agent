import os
import pandas as pd

data_dir = "dataset"
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))

# Inspect user_06 expenses by category in previous months (Nov & Dec 2025)
u06 = events_df[(events_df["user_id"] == "user_06") & (events_df["direction"] == "debit") & (events_df["status"] == "settled")].copy()
u06["month"] = u06["event_date"].str.slice(0, 7)
print("=== USER 06 MONTHLY SPENDING BY CATEGORY ===")
print(u06.groupby(["month", "category"])["amount"].sum().unstack(fill_value=0).to_string())

# Inspect user_21 expenses by category in Jan, Feb, Mar 2026
u21 = events_df[(events_df["user_id"] == "user_21") & (events_df["direction"] == "debit") & (events_df["status"] == "settled")].copy()
u21["month"] = u21["event_date"].str.slice(0, 7)
print("\n=== USER 21 MONTHLY SPENDING BY CATEGORY ===")
print(u21.groupby(["month", "category"])["amount"].sum().unstack(fill_value=0).to_string())

# Inspect user_22 expenses by category in Oct, Nov 2024
u22 = events_df[(events_df["user_id"] == "user_22") & (events_df["direction"] == "debit") & (events_df["status"] == "settled")].copy()
u22["month"] = u22["event_date"].str.slice(0, 7)
print("\n=== USER 22 MONTHLY SPENDING BY CATEGORY ===")
print(u22.groupby(["month", "category"])["amount"].sum().unstack(fill_value=0).to_string())