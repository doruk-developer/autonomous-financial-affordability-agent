import os
import sys
import pandas as pd

# Add 'code' directory directly to Python search path
sys.path.insert(0, os.path.abspath("code"))

from engine import FinancialDecisionEngine

# Initialize engine
engine = FinancialDecisionEngine(data_dir="dataset")

# Load sample requests (25 ground-truth cases)
samples_path = os.path.join("dataset", "sample_requests.csv")
samples_df = pd.read_csv(samples_path)

print("=" * 85)
print("EVALUATING FINANCIAL DECISION ENGINE AGAINST 25 GROUND-TRUTH SAMPLES")
print("=" * 85)
print(f"{'REQ_ID':<12} | {'STATUS (GT vs PRED)':<38} | {'METHOD (GT vs PRED)':<30} | {'MATCH'}")
print("-" * 85)

status_matches = 0
method_matches = 0
total_cases = len(samples_df)

for idx, row in samples_df.iterrows():
    pred = engine.evaluate_request(row)
    
    gt_status = str(row["affordability_status"])
    pred_status = str(pred["affordability_status"])
    
    gt_method = str(row["recommended_payment_method"])
    pred_method = str(pred["recommended_payment_method"])
    
    s_ok = (gt_status == pred_status)
    m_ok = (gt_method == pred_method)
    
    if s_ok: status_matches += 1
    if m_ok: method_matches += 1
    
    status_str = f"{gt_status} | {pred_status}"
    method_str = f"{gt_method} | {pred_method}"
    result_str = "OK" if (s_ok and m_ok) else ("PARTIAL" if (s_ok or m_ok) else "MISMATCH")
    
    print(f"{row['request_id']:<12} | {status_str:<38} | {method_str:<30} | {result_str}")

print("=" * 85)
print(f"Status Accuracy: {status_matches} / {total_cases} ({status_matches/total_cases*100:.1f}%)")
print(f"Method Accuracy: {method_matches} / {total_cases} ({method_matches/total_cases*100:.1f}%)")
print("=" * 85)