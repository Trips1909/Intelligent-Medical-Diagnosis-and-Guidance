import pickle
import nltk
from crf_utils import extract_features

# Load trained CRF model
crf_model = pickle.load(open('train/crf_model.pkl', 'rb'))

# Ensure required NLTK resources
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

def extract_symptoms(text):
    """
    Extracts symptom phrases from raw input text using the trained CRF model.
    """
    tokens = nltk.word_tokenize(text)
    features = extract_features(tokens)
    labels = crf_model.predict_single(features)

    symptoms = []
    current_phrase = []

    for token, label in zip(tokens, labels):
        if label == "B-SYMPTOM":
            if current_phrase:
                symptoms.append(" ".join(current_phrase))
                current_phrase = []
            current_phrase.append(token)
        elif label == "I-SYMPTOM":
            current_phrase.append(token)
        else:
            if current_phrase:
                symptoms.append(" ".join(current_phrase))
                current_phrase = []

    if current_phrase:
        symptoms.append(" ".join(current_phrase))

    return symptoms
