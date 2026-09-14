import os
import pandas as pd

dataset_dir = "dataset"

print("=== SÜTUN İSİMLERİ VE BOYUTLAR ===")
for f in sorted(os.listdir(dataset_dir)):
    if f.endswith(".csv"):
        df = pd.read_csv(os.path.join(dataset_dir, f))
        print(f"[{f}] ({len(df)} satır) -> {list(df.columns)}")

print("\n=== 16 EKSİK TUTARLI ETKİNLİK (GÖRSEL BAĞLANTILARI) ===")
events_df = pd.read_csv(os.path.join(dataset_dir, "financial_events.csv"))
images_df = pd.read_csv(os.path.join(dataset_dir, "images.csv"))
blank_events = events_df[events_df["amount"].isna()]

# Eksik tutarları images.csv ile birleştirip görelim
merged = blank_events.merge(images_df, left_on="event_id", right_on="related_event_id", how="left")
print(merged[["event_id", "user_id_x", "image_id", "description"] if "description" in merged.columns else merged.columns[:6]])

print("\n=== SAMPLE REQUESTS ÇÖZÜM FORMATI (İLK 2 SATIR) ===")
sample_df = pd.read_csv(os.path.join(dataset_dir, "sample_requests.csv"))
for col in sample_df.columns:
    print(f"  {col}: {sample_df[col].iloc[0]}")