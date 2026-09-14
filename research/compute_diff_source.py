import os
import pandas as pd

data_dir = "dataset"
profiles_df = pd.read_csv(os.path.join(data_dir, "financial_profiles.csv")).set_index("user_id")
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))
samples_df = pd.read_csv(os.path.join(data_dir, "sample_requests.csv"))

print(f"{'REQ_ID':<12} | {'DIFF':<12} | {'LAST_MO_DEBITS':<16} | {'PROTECTED_SPEND':<16} | {'RECURRING_SUM'}")
print("-" * 75)

for req_id in ["request_03", "request_04", "request_06", "request_13", "request_15", "request_19", "request_21", "request_22"]:
    row = samples_df[samples_df["request_id"] == req_id].iloc[0]
    u_id = row["user_id"]
    prof = profiles_df.loc[u_id]
    start_bal = float(prof["current_available_balance"])
    min_bal = float(prof["minimum_balance_to_keep"])
    surplus = max(0.0, start_bal - min_bal)
    safe_today = float(row["amount_safe_to_pay"])
    diff = surplus - safe_today
    
    # User debit events
    u_events = events_df[(events_df["user_id"] == u_id) & (events_df["direction"] == "debit") & (events_df["status"] == "settled")].copy()
    u_events["month"] = u_events["event_date"].str.slice(0, 7)
    
    # Last complete month debits
    months = sorted(u_events["month"].unique())
    last_mo = months[-2] if len(months) >= 2 else months[-1]
    last_mo_sum = u_events[u_events["month"] == last_mo]["amount"].sum()
    
    # Protected categories from profile
    prot_cats = [c.strip() for c in str(prof.get("expense_categories_to_protect", "")).split("|") if c.strip()]
    prot_sum = u_events[(u_events["month"] == last_mo) & (u_events["category"].isin(prot_cats))]["amount"].sum()
    
    # Recurring types (subscription, rent, utilities)
    rec_sum = u_events[(u_events["month"] == last_mo) & (u_events["event_type"].isin(["subscription", "expense"])) & (u_events["category"].str.contains("rent|util|sub|insur", case=False, na=False))]["amount"].sum()
    
    print(f"{req_id:<12} | {diff:<12.1f} | {last_mo_sum:<16.1f} | {prot_sum:<16.1f} | {rec_sum:<.1f}")