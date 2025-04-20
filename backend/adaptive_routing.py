from gpt_routing import generate_followup

def route_next_question(symptoms, diagnosis, confidence, followup_index):
    return generate_followup(diagnosis, confidence, followup_index)
