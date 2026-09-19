import json
import pandas as pd

CONFIG_PATH = "./models/xlm_roberta_classification/config.json"
CSV_PATH = "./data/raw/hinglish_robust_semantic_43x700.csv"
OUTPUT_PATH = "./data/processed/hinglish_robust_semantic_43x700_processed.csv"

# 1. Open config.json
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

# 2. Get label -> ID mapping
label2id = config["label2id"]

# 3. Open CSV
df = pd.read_csv(CSV_PATH)

# 4. Replace labels with their IDs
df["labels"] = df["labels"].map(label2id)
#./data/processed/home_intelligence_encoded.csv
# 5. Check for labels that weren't found
if df["labels"].isna().any():
    print("ERROR: Some labels were not found in config.json")
    raise ValueError("Unknown label found in CSV.")

# 6. Convert IDs to integers
df["labels"] = df["labels"].astype(int)

# 7. Save encoded CSV
df.to_csv(OUTPUT_PATH, index=False)

print(f"Done! Encoded dataset saved to: {OUTPUT_PATH}")