import os
import pandas as pd

out_path = "output.csv"
req_path = os.path.join("dataset", "requests.csv")

if not os.path.exists(out_path):
    raise FileNotFoundError(f"Missing {out_path}!")

df_out = pd.read_csv(out_path)
df_req = pd.read_csv(req_path)

print("=" * 60)
print("SUBMISSION SCHEMA & INTEGRITY VALIDATION")
print("=" * 60)

# 1. Row count check
print(f"Row count: {len(df_out)} (Expected: {len(df_req)}) -> {'PASS' if len(df_out) == len(df_req) else 'FAIL'}")

# 2. Exact Column Order
expected_cols = [
    "request_id",
    "amount_safe_to_pay",
    "affordability_status",
    "recommended_payment_method",
    "payment_plan",
    "earliest_date_for_full_payment",
    "spending_changes_needed",
    "decision_explanation"
]
print(f"Columns match exactly: {'PASS' if list(df_out.columns) == expected_cols else 'FAIL'}")

# 3. Check for unexpected NaN values (only earliest_date can be empty)
crit_cols = ["request_id", "amount_safe_to_pay", "affordability_status", "recommended_payment_method", "payment_plan", "spending_changes_needed", "decision_explanation"]
has_nan = df_out[crit_cols].isna().any().any()
print(f"No invalid NaN values in critical columns: {'PASS' if not has_nan else 'FAIL'}")

# 4. Check status & method sets
valid_statuses = {"affordable_now", "affordable_with_plan", "affordable_later", "not_affordable"}
valid_methods = {"full_payment", "partial_payment", "installments", "wait", "not_recommended"}

status_ok = set(df_out["affordability_status"]).issubset(valid_statuses)
method_ok = set(df_out["recommended_payment_method"]).issubset(valid_methods)

print(f"All affordability_status values valid: {'PASS' if status_ok else 'FAIL'}")
print(f"All recommended_payment_method values valid: {'PASS' if method_ok else 'FAIL'}")
print("=" * 60)
print("ALL VALIDATION CHECKS COMPLETED!")