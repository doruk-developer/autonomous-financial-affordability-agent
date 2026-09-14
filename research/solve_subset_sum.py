import os
import itertools
import pandas as pd

data_dir = "dataset"
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))

# User 22 November debit events between day 5 and 15
u22 = events_df[(events_df["user_id"] == "user_22") & (events_df["direction"] == "debit")].copy()
u22["day"] = pd.to_datetime(u22["event_date"]).dt.day
nov_events = u22[(u22["event_date"] >= "2024-11-01") & (u22["event_date"] <= "2024-11-30") & (u22["day"] >= 5) & (u22["day"] <= 15)]

print(f"=== TESTING SUBSET SUM FOR USER 22 (TARGET: 114.04 EUR) ===")
target = 114.04
items = nov_events[["description", "category", "amount"]].to_dict("records")

found = False
for r in range(1, len(items) + 1):
    for combo in itertools.combinations(items, r):
        s = sum(x["amount"] for x in combo)
        if abs(s - target) < 0.01:
            print(f"\n[EXACT MATCH FOUND! (Count: {len(combo)})]")
            for x in combo:
                print(f"  + {x['description']:<30} | {x['category']:<15} | {x['amount']}")
            found = True
            break
    if found:
        break

if not found:
    print("No exact single-month match. Checking category aggregates...")
    cat_sums = nov_events.groupby("category")["amount"].sum().to_dict()
    print("Nov 5-15 Category sums:", cat_sums)