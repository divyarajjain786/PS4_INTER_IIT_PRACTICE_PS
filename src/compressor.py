import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

src_model_dir = "./models/"
final_quant_dir = "./models/xmlr_int8/"

print("Step 1: Loading original FP32 model into memory...")

model_fp32 = AutoModelForSequenceClassification.from_pretrained(src_model_dir)
tokenizer = AutoTokenizer.from_pretrained(src_model_dir)

print("Step 2: Quantizing model to INT8 via PyTorch Dynamic Quantization...")


model_int8 = torch.quantization.quantize_dynamic(model_fp32, {torch.nn.Linear}, dtype=torch.qint8)

print(f"Step 3: Saving the new INT8 model to {final_quant_dir}...")
# Create the directory if it doesn't exist
os.makedirs(final_quant_dir, exist_ok=True)

# Save the quantized weights and tokenizer configuration files
model_int8.save_pretrained(final_quant_dir)
tokenizer.save_pretrained(final_quant_dir)

print("\n Success! Your original model remains untouched in standard FP32.")
print(f" Your new PyTorch INT8 model is saved in: {final_quant_dir}")
