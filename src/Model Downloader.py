#Model Downloader
from transformers import AutoTokenizer, AutoModel

model_name = "hotchpotch/mMiniLMv2-L6-H384"
# Replace this with your desired local directory path
local_directory = "./models/mMiniLMv2_Student"

# Download tokenizer and model from Hugging Face
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Save both to your specific local path
tokenizer.save_pretrained(local_directory)
model.save_pretrained(local_directory)

print(f"Model and tokenizer successfully saved to: {local_directory}")
