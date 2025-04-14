from gpt_routing import generate_followup

def route_next_question(symptoms, diagnosis, confidence):
    return generate_followup(symptoms, diagnosis, confidence)
