import pickle
import numpy as np
import pandas as pd
import nltk

# Load models and preprocessing artifacts
xgb = pickle.load(open('train/xgb_model.pkl', 'rb'))
lgbm = pickle.load(open('train/lgbm_model.pkl', 'rb'))
catboost = pickle.load(open('train/catboost_model.pkl', 'rb'))
preprocessor = pickle.load(open('train/preprocessor.pkl', 'rb'))
crf = pickle.load(open('train/crf_model.pkl', 'rb'))
label_encoder = pickle.load(open('train/label_encoder.pkl', 'rb'))

labels = list(label_encoder.classes_)

# NLTK Downloads
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# 🔍 CRF Feature Extraction
def extract_features(tokens):
    pos_tags = nltk.pos_tag(tokens)
    return [
        {
            'word': word,
            'pos': pos,
            'pos_prefix': pos[0],
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

# 🧠 Keyword Extraction using CRF
def extract_keywords_from_text(text):
    tokens = nltk.word_tokenize(text)
    features = extract_features(tokens)
    label_seq = crf.predict([features])[0]

    keywords, current = [], []
    for token, label in zip(tokens, label_seq):
        if label == "B-SYMPTOM":
            if current:
                keywords.append(" ".join(current))
                current = []
            current.append(token)
        elif label == "I-SYMPTOM":
            current.append(token)
        else:
            if current:
                keywords.append(" ".join(current))
                current = []
    if current:
        keywords.append(" ".join(current))
    return keywords

# 🚀 Mode 1: Free-text → CRF → Symptoms → Classification
def predict_diagnosis(user_text, return_all=False):
    keywords = extract_keywords_from_text(user_text)
    symptom_summary = ", ".join(keywords)

    print(f"\n[DEBUG] Extracted Keywords: {symptom_summary}")

    structured_input = pd.DataFrame([{"symptom_text": symptom_summary}])
    X_input = preprocessor.transform(structured_input)

    return _ensemble_predict(X_input, return_all)

# 🚀 Mode 2: Structured Form + Q1–Q10 (Direct)
def predict_diagnosis_from_structured(input_dict, return_all=False):
    X_input = preprocessor.transform([input_dict])
    return _ensemble_predict(X_input, return_all)

# 🧮 Core Weighted Prediction Logic
def _ensemble_predict(X_input, return_all=False):
    proba_xgb = xgb.predict_proba(X_input)
    proba_lgbm = lgbm.predict_proba(X_input)
    proba_cat = catboost.predict_proba(X_input)

    avg_proba = (0.5 * proba_xgb + 0.25 * proba_lgbm + 0.25 * proba_cat)[0]
    prediction = labels[np.argmax(avg_proba)]
    confidence = round(np.max(avg_proba) * 100, 2)

    print(f"[DEBUG] Class Probabilities: {dict(zip(labels, avg_proba))}")

    if return_all:
        return dict(zip(labels, avg_proba)), confidence, prediction
    return prediction, confidence
