import os
import sys
import pandas as pd
import nltk
import pickle
from sklearn_crfsuite import CRF

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from crf_utils import identity

# Load dataset
df = pd.read_csv("data/Mental_Health_Symptom_Dataset.csv")

X, y = [], []
for symptom_str, label in zip(df["symptoms"], df["label"]):
    tokens = [s.strip() for s in symptom_str.split(",")]
    features = extract_features(tokens)
    labels = ["SYMPTOM"] * len(tokens)
    X.append(features)
    y.append(labels)

# Train CRF
crf = CRF()
crf.fit(X, y)

# Save model
with open("train/crf_model.pkl", "wb") as f:
    pickle.dump(crf, f)
