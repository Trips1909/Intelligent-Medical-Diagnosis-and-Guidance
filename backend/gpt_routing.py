import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_followup(symptoms, diagnosis, confidence):
    prompt = f"""
You're a supportive mental health assistant.
Symptoms detected: {', '.join(symptoms)}.
The system currently predicts: {diagnosis} with {confidence}% confidence.

Ask a medically relevant, polite follow-up question to clarify if this diagnosis is correct.
Do not assume the prediction is final. Consider overlapping traits of anxiety, OCD, and autism.
"""
    print("\n[DEBUG] GPT prompt:\n", prompt)

    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful, supportive mental health assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()
