from datasets import load_dataset
from transformers import AutoTokenizer, DataCollatorWithPadding, AutoModelForSequenceClassification, TrainingArguments, Trainer, set_seed
# FIX: Import load directly under an alias to completely avoid naming collisions with local files or methods
from evaluate import load as hf_evaluate_load
from data import load

class TrainingClass:
    def __init__(self):
        self.LOCAL_PATH = "./models/xlm_roberta_classification"

        self.tokenizer = AutoTokenizer.from_pretrained(self.LOCAL_PATH)
        self.data_collator = DataCollatorWithPadding(tokenizer=self.tokenizer)
        
        # FIX: Added ignore_mismatched_sizes=True so changing labels to 43 won't cause a size mismatch crash
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.LOCAL_PATH, 
            num_labels=43, 
            ignore_mismatched_sizes=True
        )

        # Using the collision-proof function alias
        self.accuracy = hf_evaluate_load("accuracy")
        self.f1 = hf_evaluate_load("f1")
        set_seed(42)

    def preprocess_function(self, examples):
        return self.tokenizer(examples["Input"], truncation=True, padding = "longest")

    def compute_metrics(self, eval_pred):
        logits, labels = eval_pred
        predictions = logits.argmax(axis=-1)
        accuracy = self.accuracy.compute(predictions=predictions, references=labels)
        f1 = self.f1.compute(predictions=predictions, references=labels, average="macro")
        return {"accuracy": accuracy["accuracy"], "f1": f1["f1"]}

    def train(self):
        loader = load()
        Tokenized_Data = loader.getData().map(self.preprocess_function, batched=True)

        # Note: Your learning rate (2e-5) is perfectly set now for safe transformer fine-tuning!
        train_args = TrainingArguments(output_dir="./results", learning_rate=2e-5, per_device_train_batch_size=10, per_device_eval_batch_size=10, num_train_epochs=3, eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=False, logging_steps=50, report_to="none")
        
        trainer = Trainer(model=self.model, args=train_args, data_collator=self.data_collator, train_dataset=Tokenized_Data["train"], eval_dataset=Tokenized_Data["test"], processing_class=self.tokenizer, compute_metrics=self.compute_metrics)
        
        trainer.train()
        trainer.save_model(self.LOCAL_PATH)
        self.tokenizer.save_pretrained(self.LOCAL_PATH)

# Properly structured execution block
if __name__ == "__main__":
    Trai = TrainingClass()
    Trai.train()
