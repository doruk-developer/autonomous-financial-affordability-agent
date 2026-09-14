import os
import pandas as pd

samples_df = pd.read_csv(os.path.join("dataset", "sample_requests.csv"))
profiles_df = pd.read_csv(os.path.join("dataset", "financial_profiles.csv")).set_index("user_id")

target_cases = ["request_03", "request_04", "request_05", "request_06", "request_11", "request_13", "request_14", "request_19", "request_20", "request_21"]

print(f"{'REQ_ID':<12} | {'GT_SAFE':<10} | {'REQ_AMT':<10} | {'GT_STATUS':<22} | {'GT_METHOD':<18}")
print("-" * 80)

for req_id in target_cases:
    row = samples_df[samples_df["request_id"] == req_id].iloc[0]
    print(f"{req_id:<12} | {row['amount_safe_to_pay']:<10.1f} | {row['requested_amount']:<10.1f} | {row['affordability_status']:<22} | {row['recommended_payment_method']:<18}")
    print(f"  -> Explanation: {row['decision_explanation']}")
    print(f"  -> Spending Changes: {row['spending_changes_needed']}")
    print("-" * 80)