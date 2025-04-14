import pickle
import numpy as np
from crf_utils import identity

xgb = pickle.load(open('train/xgb_model.pkl', 'rb'))
lgbm = pickle.load(open('train/lgbm_model.pkl', 'rb'))
catboost = pickle.load(open('train/catboost_model.pkl', 'rb'))
vectorizer = pickle.load(open('train/vectorizer.pkl', 'rb'))
labels = ['Anxiety', 'OCD', 'Autism']

def predict_diagnosis(symptoms, return_all=False):
    X = vectorizer.transform([symptoms]).astype("float32")
    probs = [model.predict_proba(X) for model in [xgb, lgbm, catboost]]
    avg_proba = np.mean(probs, axis=0)

    print("\n[DEBUG] Raw class probabilities:", dict(zip(labels, avg_proba)))

    pred = labels[np.argmax(avg_proba)]
    conf = round(np.max(avg_proba) * 100, 2)

    if return_all:
        return dict(zip(labels, avg_proba)), conf, pred
    return pred, conf
