import re

# ✨ Rule-based scoring logic
def score_response(text):
    """
    Assigns a delta score based on the nature of the response.
    Returns an integer from -5 to +5.
    """
    text = text.lower().strip()

    strong_positive = [
        "absolutely", "definitely", "always", "very much", "frequently", "yes", "i do", "of course", "every time", "often"
    ]

    moderate_positive = [
        "sometimes", "occasionally", "maybe", "could be", "at times", "depends", "partially", "not always", "not sure"
    ]

    negative = [
        "no", "never", "i don't", "not really", "rarely", "i'm not sure", "hardly", "uncertain"
    ]

    # Match exact phrases or loose patterns
    if any(p in text for p in strong_positive):
        return +3
    elif any(p in text for p in moderate_positive):
        return +1
    elif any(p in text for p in negative):
        return -2
    else:
        return 0  # Default if inconclusive


def adjust_confidence(base_confidence, gpt_responses):
    """
    Adjusts base confidence using up to 5 follow-up responses.
    Returns adjusted confidence as float.
    """
    delta = 0
    for response in gpt_responses:
        delta += score_response(response)

    new_conf = base_confidence + delta

    # Clamp the confidence to range [0, 100]
    new_conf = max(0, min(100, new_conf))
    return round(new_conf, 2)
