import os
import sys
import pandas as pd

sys.path.insert(0, os.path.abspath("code"))
from engine import FinancialDecisionEngine

engine = FinancialDecisionEngine(data_dir="dataset")
samples_df = pd.read_csv(os.path.join("dataset", "sample_requests.csv"))

mismatch_ids = ["request_03", "request_04", "request_05", "request_06", "request_11", "request_13", "request_14", "request_19", "request_20", "request_21"]

print("=== DEEP DIAGNOSTIC OF THE 10 TARGET CASES ===")
for req_id in mismatch_ids:
    row = samples_df[samples_df["request_id"] == req_id].iloc[0]
    pred = engine.evaluate_request(row)
    
    print(f"\n[{req_id}] User: {row['user_id']} | Date: {row['request_date']} | Target: {row['desired_completion_date']}")
    print(f"  Req Amt: {row['requested_amount']} | GT Safe: {row['amount_safe_to_pay']} | Pred Safe: {pred['amount_safe_to_pay']}")
    print(f"  GT Status : {row['affordability_status']:<22} | Pred Status : {pred['affordability_status']}")
    print(f"  GT Method : {row['recommended_payment_method']:<22} | Pred Method : {pred['recommended_payment_method']}")
    print(f"  GT Earliest Date: {row['earliest_date_for_full_payment']} | Pred Earliest Date: {pred['earliest_date_for_full_payment']}")
    print(f"  GT Changes: {row['spending_changes_needed']} | Pred Changes: {pred['spending_changes_needed']}")