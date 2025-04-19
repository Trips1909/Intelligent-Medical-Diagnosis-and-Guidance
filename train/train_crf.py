import os
import sys
import pandas as pd
import pickle
import nltk
from sklearn_crfsuite import CRF

# Download POS tagger if not already available
nltk.download('averaged_perceptron_tagger')

# Optional: Add backend dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Define POS-enhanced feature extractor
def extract_features(tokens):
    pos_tags = nltk.pos_tag(tokens)
    return [
        {
            'word': word,
            'pos': pos,
            'pos_prefix': pos[0],  # N for NN, V for VB, etc.
            'is_upper': word.isupper(),
            'is_title': word.istitle(),
            'is_digit': word.isdigit(),
            'suffix3': word[-3:],
            'prefix3': word[:3],
            'prev_word': '' if i == 0 else tokens[i - 1],
            'next_word': '' if i == len(tokens) - 1 else tokens[i + 1]
        }
        for i, (word, pos) in enumerate(pos_tags)
    ]

# Load labeled BIO-tagged dataset
df = pd.read_csv("data/crf_training_dataset.csv")

# Group by sentence_id
grouped = df.groupby("sentence_id")

X, y = [], []

for _, group in grouped:
    tokens = group["token"].tolist()
    labels = group["label"].tolist()
    X.append(extract_features(tokens))
    y.append(labels)

# Train CRF
crf = CRF()
crf.fit(X, y)

# Save trained model
os.makedirs("train", exist_ok=True)
with open("train/crf_model.pkl", "wb") as f:
    pickle.dump(crf, f)
