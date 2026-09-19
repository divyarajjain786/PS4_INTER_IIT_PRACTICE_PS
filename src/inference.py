from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import time
import normalizer

class Predictor:

    def __init__(self):
        #self.LOCAL_PATH = "./models/xlm_roberta_classification"
        self.LOCAL_PATH = "./models/xlm_roberta_classification"
        self.model = AutoModelForSequenceClassification.from_pretrained(self.LOCAL_PATH)
        self.tokenizer = AutoTokenizer.from_pretrained(self.LOCAL_PATH)

        self.classifier = pipeline("text-classification", model= self.model, tokenizer = self.tokenizer)

        
    def predict(self, input = "Ghatiya hai"):
        return(self.classifier(input, top_k =None))

#if __name__ == "main":
predictor = Predictor()
inp = input("Enter text:")
inp =  normalizer.normalize_text(inp)
for _ in range(5):
    predictor.predict(input= inp)

times = []

for _ in range(100):
    start = time.perf_counter()
    predictor.predict(input = inp)
    times.append((time.perf_counter() - start) * 1000)

print(f"Average latency: {sum(times)/len(times):.2f} ms")
result = predictor.predict(input = inp)
print(result)