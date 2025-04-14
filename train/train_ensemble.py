import os
import sys
import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from crf_utils import identity

# Load dataset
df = pd.read_csv("data/Mental_Health_Symptom_Dataset.csv")
df["symptoms"] = df["symptoms"].apply(lambda s: s.split(","))

# Vectorize symptom tokens
vectorizer = CountVectorizer(tokenizer=identity, preprocessor=identity)
X_vec = vectorizer.fit_transform(df["symptoms"])

# 🔧 Convert to float32 for LightGBM compatibility
X_vec = X_vec.astype("float32")

# Encode string labels numerically
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df["label"])

# Initialize classifiers
xgb = XGBClassifier(eval_metric='mlogloss')
lgbm = LGBMClassifier()
catboost = CatBoostClassifier(verbose=0)

# Train models
xgb.fit(X_vec, y)
lgbm.fit(X_vec, y)
catboost.fit(X_vec, y)

# Save models and preprocessing objects
with open("train/xgb_model.pkl", "wb") as f:
    pickle.dump(xgb, f)
with open("train/lgbm_model.pkl", "wb") as f:
    pickle.dump(lgbm, f)
with open("train/catboost_model.pkl", "wb") as f:
    pickle.dump(catboost, f)
with open("train/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)
with open("train/label_encoder.pkl", "wb") as f:
    pickle.dump(label_encoder, f)
