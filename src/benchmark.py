import os
import time
import pandas as pd
import torch
from sklearn.metrics import accuracy_score, f1_score
from transformers import pipeline


MODEL_PATH = "./models/xlm_roberta_classification"
TEST_FILE = "./data/processed/test.csv"
RESULT_FILE = "./results/XLM-R/benchmark_results.csv"


# Load test data
data = pd.read_csv(TEST_FILE)

texts = data["Input"].astype(str).tolist()
labels = data["label"].tolist()


# Load model
device = 0 if torch.cuda.is_available() else -1

classifier = pipeline("text-classification",model=MODEL_PATH,tokenizer=MODEL_PATH,device=device)


# Warm-up
for text in texts[:10]:
    classifier(text)


# Predict
predictions = []
latencies = []

for text in texts:
    start = time.perf_counter()
    result = classifier(text)[0]
    if torch.cuda.is_available():
        torch.cuda.synchronize()
    end = time.perf_counter()
    predictions.append(int(result["label"].split("_")[-1]))
    latencies.append((end - start) * 1000)


# Metrics
accuracy = accuracy_score(labels, predictions)

macro_f1 = f1_score(labels,predictions,average="macro")

weighted_f1 = f1_score(labels,predictions,average="weighted")


# Results
results = pd.DataFrame({"Model": [MODEL_PATH],"\nTest samples": [len(labels)],"\nAccuracy": [accuracy],"\nMacro F1": [macro_f1],"\nWeighted F1": [weighted_f1],"\nAverage latency (ms)": [sum(latencies) / len(latencies)],"\nDevice": ["GPU" if torch.cuda.is_available() else "CPU"]})


# Save
os.makedirs("./results", exist_ok=True)

results.to_csv(RESULT_FILE,index=False)

print(results)
print(f"\nSaved to: {RESULT_FILE}")