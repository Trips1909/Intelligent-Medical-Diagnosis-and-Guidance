def get_recommendation(diagnosis):
    recs = {
        "Anxiety": "Practice mindfulness, try CBT, and consider therapy.",
        "OCD": "CBT and exposure therapy are effective treatments.",
        "Autism": "Seek behavioral therapy and social skills support."
    }
    return recs.get(diagnosis, "Consult a mental health professional.")
