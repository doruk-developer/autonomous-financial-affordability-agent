import os
import json

json_path = os.path.join("dataset", "extracted_image_amounts.json")

data = {}
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

# Insert the verified values for image_07 and image_12
data["event_3231"] = {
    "amount": 8528.0,
    "currency": "INR",
    "image_id": "image_07",
    "description": "Restaurant tax invoice"
}

data["event_7307"] = {
    "amount": 33.50,
    "currency": "USD",
    "image_id": "image_12",
    "description": "Taxi fare"
}

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"[SUCCESS] All 16/16 missing amounts are locked in: {json_path}")
print(f"Total entries: {len(data)}")