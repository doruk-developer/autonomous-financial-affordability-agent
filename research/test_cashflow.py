import os
import json
import pandas as pd
import numpy as np

# Load core datasets
data_dir = "dataset"
profiles_df = pd.read_csv(os.path.join(data_dir, "financial_profiles.csv"))
events_df = pd.read_csv(os.path.join(data_dir, "financial_events.csv"))
rates_df = pd.read_csv(os.path.join(data_dir, "exchange_rates.csv"))
options_df = pd.read_csv(os.path.join(data_dir, "request_payment_options.csv"))
messages_df = pd.read_csv(os.path.join(data_dir, "messages.csv"))
samples_df = pd.read_csv(os.path.join(data_dir, "sample_requests.csv"))

# Load extracted image amounts
extracted_images = {}
img_json_path = os.path.join(data_dir, "extracted_image_amounts.json")
if os.path.exists(img_json_path):
    with open(img_json_path, "r", encoding="utf-8") as f:
        extracted_images = json.load(f)

print("[INIT] Datasets and extracted amounts loaded successfully.")
print(f"Total Profiles: {len(profiles_df)} | Total Events: {len(events_df)}")
print(f"Event directions: {events_df['direction'].unique()}")
print(f"Event statuses: {events_df['status'].unique()}")
print(f"Flexibility types: {events_df['flexibility'].unique()}")
print(f"Sample ground truth count: {len(samples_df)}")