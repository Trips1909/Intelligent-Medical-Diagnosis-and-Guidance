import re

# ✨ Rule-based scoring logic (5 levels)
def score_response(text):
    """
    Assigns a delta score from +5 to -2 based on the nature of the GPT follow-up response.
    """
    text = text.lower().strip()

    strong_positive = [
        "absolutely", "definitely", "without a doubt", "for sure", "always", "every time", "very frequently", "strongly agree"
    ]

    mild_positive = [
        "often", "yes", "frequently", "i do", "of course", "likely", "generally", "mostly", "i think so"
    ]

    neutral = [
        "maybe", "sometimes", "occasionally", "not sure", "could be", "depends", "at times", "possibly", "partially"
    ]

    mild_negative = [
        "not really", "i don't think so", "rarely", "i guess not", "hardly", "seldom", "not usually", "unlikely"
    ]

    strong_negative = [
        "never", "absolutely not", "i don't", "i never", "strongly disagree", "definitely not"
    ]

    if any(p in text for p in strong_positive):
        return +5
    elif any(p in text for p in mild_positive):
        return +2
    elif any(p in text for p in neutral):
        return 0
    elif any(p in text for p in mild_negative):
        return -1
    elif any(p in text for p in strong_negative):
        return -2
    else:
        return 0  # default fallback if unrecognized

# 🔄 Apply scoring to all responses and adjust base confidence
def adjust_confidence(base_confidence, gpt_responses):
    """
    Adjusts base confidence using GPT-based follow-up answers.
    Returns adjusted confidence (clamped 0-100).
    """
    delta = sum(score_response(resp) for resp in gpt_responses)
    new_conf = base_confidence + delta
    return round(max(0, min(100, new_conf)), 2)
