from datasets import load_dataset
class load:
    def __init__(self, path ="./data/processed/home_intelligence_21500_roman_hindi_semantic_noise_processed.csv"):
        self.data = load_dataset("csv", data_files=path)["train"]
        self.data = self.data.train_test_split(test_size=0.2, seed=42)

    def getData(self):
        return self.data
    