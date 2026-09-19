import os
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, ConcatDataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AdamW, get_scheduler
from datasets import load_dataset

# 1. Configuration & Paths
TEACHER_MODEL_PATH = "./models/xlm-roberta-base" 
STUDENT_MODEL_PATH = "./models/models/mMiniLMv2_Student"
OUTPUT_DIR = "./models/distilled_ready_to_go_classifier"

# Provide paths to your local text files (e.g., CSV) containing noisy Hinglish
DATASET_PATHS = ["./data/processed/hinglish_robust_semantic_43x700_processed.csv", "./data/processed/home_intelligence_21500_roman_hindi_semantic_noise_processed.csv"]

NUM_LABELS = 43
BATCH_SIZE = 16
EPOCHS = 3
LEARNING_RATE = 5e-5
MAX_LENGTH = 128
ALPHA_MSE = 1.0  

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained(TEACHER_MODEL_PATH)

def custom_tokenize_function(examples):
    # Adjust "text" if your CSV column name is different
    return tokenizer(examples["Inputs"], truncation=True, max_length=MAX_LENGTH, padding="longest")

processed_datasets = []
for path in DATASET_PATHS:
    if not os.path.exists(path):
        print(f"Skipping missing path: {path}")
        continue
    
    raw_ds = load_dataset("csv", data_files=path, split="train")
    tokenized_ds = raw_ds.map(custom_tokenize_function, batched=True, remove_columns=["Inputs"])
    tokenized_ds.set_format(type="torch", columns=["input_ids", "attention_mask"])
    processed_datasets.append(tokenized_ds)

combined_dataset = ConcatDataset(processed_datasets)
train_loader = DataLoader(combined_dataset, batch_size=BATCH_SIZE, shuffle=True)


# This copies the classification head architecture template
teacher_model = AutoModelForSequenceClassification.from_pretrained(TEACHER_MODEL_PATH, num_labels=NUM_LABELS).to(device)
student_model = AutoModelForSequenceClassification.from_pretrained(STUDENT_MODEL_PATH, num_labels=NUM_LABELS).to(device)

student_model.config.id2label = teacher_model.config.id2label
student_model.config.label2id = teacher_model.config.label2id

teacher_model.eval()
for param in teacher_model.parameters():
    param.requires_grad = False

student_model.train()

#Projection Layer (Aligning Hidden Dimension Sizes)
projection_layer = nn.Linear(384, 768).to(device)

#Optimizer & Loss Criteria
optimizer = AdamW(list(student_model.parameters()) + list(projection_layer.parameters()), lr=LEARNING_RATE)
mse_criterion = nn.MSELoss()

num_training_steps = EPOCHS * len(train_loader)
lr_scheduler = get_scheduler("linear", optimizer=optimizer, num_warmup_steps=int(0.1 * num_training_steps), num_training_steps=num_training_steps)

#Training
print("Starting Out-Of-Box Distillation Training Pipeline (Float32)...")
for epoch in range(EPOCHS):
    total_loss = 0
    for step, batch in enumerate(train_loader):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        
        optimizer.zero_grad()
        
        with torch.no_grad():
            teacher_outputs = teacher_model(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True)
            teacher_hidden = teacher_outputs.hidden_states[-1]
            
        student_outputs = student_model(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True)
        student_hidden = student_outputs.hidden_states[-1]
        
        projected_student_hidden = projection_layer(student_hidden)
        
        # Mask out padding tokens so loss is computed purely on real semantic text tokens
        mask = attention_mask.unsqueeze(-1).expand_as(teacher_hidden).float()
        loss = mse_criterion(projected_student_hidden * mask, teacher_hidden * mask)
        
        loss.backward()
        optimizer.step()
        lr_scheduler.step()
        
        total_loss += loss.item()
        
        if step % 100 == 0:
            print(f"Epoch: {epoch+1}/{EPOCHS} | Step: {step}/{len(train_loader)} | Current MSE Loss: {loss.item():.4f}")
            
    print(f"--- Epoch {epoch+1} Complete. Average Loss: {total_loss / len(train_loader):.4f} ---")

#Saving the student
student_model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f"Distillation complete! Ready-to-go model saved to: {OUTPUT_DIR}")
