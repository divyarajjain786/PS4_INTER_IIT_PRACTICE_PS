# The Polyglot's Shorthand

Romanized/code-mixed South Asian text classification using XLM-RoBERTa.

## Overview

This project trains an XLM-RoBERTa sequence-classification model on Romanized Hindi / Hinglish text.

The dataset contains 43 intent classes and noisy text including Romanized Hindi, code-mixing, spelling variation, typos, slang, emojis, and punctuation.

The trained model is stored at:

./models/xlm_roberta_classification

## Project Structure

.
├── train.py
├── inference.py
├── compressor.py
├── requirements.txt
├── data/
│   └── processed/
├── models/
│   └── xlm_roberta_classification/
└── results/


## Installation

```bash
pip install -r requirements.txt
```

## Training

```bash
python train.py
```

The training script loads the processed dataset through the project's data loader, tokenizes the `Input` text using XLM-R, and trains a 43-class sequence-classification model.

The trained model is saved to:

```text
./models/xlm_roberta_classification
```

## Inference

```bash
python inference.py
```

The inference script loads the trained model and tokenizer and performs text classification.

## Model

The project uses XLM-RoBERTa for multilingual sequence classification with 43 output classes. Evaluation includes accuracy and macro F1.

## Compression

`compressor.py` contains the model-compression workflow used in the project.

Compression should be compared with the original model using the same test set and hardware so that accuracy and latency comparisons are meaningful.

## Evaluation

The benchmark should report:

- Accuracy
- Macro F1
- Weighted F1
- Average inference latency
- Test-set size
- Device used

But, due to time constraints, was unable to upload the report

Results are saved under:

```text
./results/
```

## Dataset

Processed datasets used in the project include:

```text
./data/processed/hinglish_robust_semantic_43x700_processed.csv
./data/processed/home_intelligence_21500_roman_hindi_semantic_noise_processed.csv
```

The training code expects an `Input` text field and uses the project's data loader to prepare the dataset and labels.


# How to run:
The entire source code along with models is on:
 https://drive.google.com/drive/folders/1HaKRcK9lvjYc1yIqT61fFK_A5rji7PiX?usp=sharing

Import this folder in Google colab and choose T4 GPU as runtime.
Execute the following codes in order:
%cd /content/drive/MyDrive/Polyglot_Inter_IIT_PS4_2026_PRE_SELECTION/polyglot-shorthand/
!pip install torch transformers datasets accelerate sentencepiece
!python ./src/inference.py
## Notes

The model is designed for noisy Romanized/code-mixed text rather than clean standard Hindi or English.

