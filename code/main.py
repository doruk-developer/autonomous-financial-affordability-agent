import os
import sys
import pandas as pd
from datetime import datetime

# Ensure 'code' directory is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import FinancialDecisionEngine

def main():
    print("=" * 70)
    print("STARTING FULL PREDICTION PIPELINE: BUY OR WAIT?")
    print("=" * 70)

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(repo_root, "dataset")
    requests_path = os.path.join(data_dir, "requests.csv")
    output_path = os.path.join(repo_root, "output.csv")

    if not os.path.exists(requests_path):
        raise FileNotFoundError(f"Input file not found: {requests_path}")

    # Initialize the calibrated engine
    engine = FinancialDecisionEngine(data_dir=data_dir)

    # Read evaluation requests
    df_req = pd.read_csv(requests_path)
    total_reqs = len(df_req)
    print(f"[LOAD] Successfully loaded {total_reqs} requests from {requests_path}")

    results = []
    start_time = datetime.now()

    for idx, row in df_req.iterrows():
        res = engine.evaluate_request(row)
        results.append(res)
        if (idx + 1) % 50 == 0 or (idx + 1) == total_reqs:
            print(f"[PROGRESS] Processed {idx + 1} / {total_reqs} requests...")

    # Build output DataFrame with EXACT schema required by challenge
    df_out = pd.DataFrame(results)[[
        "request_id",
        "amount_safe_to_pay",
        "affordability_status",
        "recommended_payment_method",
        "payment_plan",
        "earliest_date_for_full_payment",
        "spending_changes_needed",
        "decision_explanation"
    ]]

    # Ensure earliest_date_for_full_payment uses empty string for non-applicable cases
    df_out["earliest_date_for_full_payment"] = df_out["earliest_date_for_full_payment"].fillna("")

    # Save output.csv to repository root
    df_out.to_csv(output_path, index=False)

    duration = (datetime.now() - start_time).total_seconds()
    print("=" * 70)
    print(f"[SUCCESS] Complete predictions successfully generated!")
    print(f"  - Target file: {output_path}")
    print(f"  - Rows: {len(df_out)} / {total_reqs}")
    print(f"  - Elapsed time: {duration:.2f} seconds")
    print("=" * 70)

    # Quick sanity validation
    print("\nAffordability Status Distribution:")
    print(df_out["affordability_status"].value_counts())
    print("\nRecommended Payment Method Distribution:")
    print(df_out["recommended_payment_method"].value_counts())

if __name__ == "__main__":
    main()