import pickle
import nltk
from crf_utils import extract_features

crf_model = pickle.load(open('train/crf_model.pkl', 'rb'))

def extract_symptoms(tokens):
    labels = crf_model.predict_single(extract_features(tokens))
    return [t for t, l in zip(tokens, labels) if l == 'SYMPTOM']