import nltk

def identity(x):
    return x

def extract_features(tokens):
    """
    Extracts a set of features for each token in a sentence to be used with CRF models.
    
    Features include:
    - POS tag
    - Case features
    - Prefixes and suffixes
    - Neighboring words
    """
    pos_tags = nltk.pos_tag(tokens)
    return [
        {
            'word': token,
            'word.lower()': token.lower(),
            'prefix3': token[:3],
            'suffix3': token[-3:],
            'is_title': token.istitle(),
            'is_upper': token.isupper(),
            'is_digit': token.isdigit(),
            'postag': pos,
            'postag_prefix': pos[0],
            'prev_word': '' if i == 0 else tokens[i - 1],
            'next_word': '' if i == len(tokens) - 1 else tokens[i + 1]
        }
        for i, (token, pos) in enumerate(pos_tags)
    ]