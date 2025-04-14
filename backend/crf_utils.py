import nltk

def identity(x):
    return x

def extract_features(tokens):
    return [{
        'word.lower()': w.lower(),
        'postag': pos,
        'is_title': w.istitle(),
        'is_upper': w.isupper()
    } for w, pos in nltk.pos_tag(tokens)]