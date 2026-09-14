import os
import pandas as pd

samples_path = os.path.join("dataset", "sample_requests.csv")
df = pd.read_csv(samples_path)

print(f"=== SAMPLE REQUESTS OVERVIEW ({len(df)} Cases) ===\n")
print("Affordability Status Distribution:")
print(df["affordability_status"].value_counts())
print("\nRecommended Payment Method Distribution:")
print(df["recommended_payment_method"].value_counts())

print("\n" + "="*80)
print("DETAILED LOOK AT SAMPLE CASES:")
print("="*80)

for idx, row in df.iterrows():
    print(f"\n[Case {idx+1}] ID: {row['request_id']} | User: {row['user_id']} | Date: {row['request_date']}")
    print(f"  Request: {row['requested_amount']} | Allows Partial: {row['allows_partial_payment']} | Target Date: {row['desired_completion_date']}")
    print(f"  OUTPUT:")
    print(f"    - Safe Today: {row['amount_safe_to_pay']}")
    print(f"    - Status: {row['affordability_status']}")
    print(f"    - Method: {row['recommended_payment_method']}")
    print(f"    - Plan: {row['payment_plan']}")
    print(f"    - Earliest Full Date: {row['earliest_date_for_full_payment']}")
    print(f"    - Spending Changes: {row['spending_changes_needed']}")
    print(f"    - Explanation: {row['decision_explanation']}")