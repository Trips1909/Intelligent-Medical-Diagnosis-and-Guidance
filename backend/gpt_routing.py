import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_followup(diagnosis, confidence, followup_index):
    """
    Generate a varied and diagnosis-specific follow-up question that does NOT resemble the general hardcoded ones.
    """

    base_prompt = f"""
You are a supportive, medically-aware mental health assistant.

Current diagnosis: {diagnosis}
Confidence: {confidence}%

Avoid repeating common screening questions like:
- Worrying excessively
- Social discomfort
- Sleep irregularity
- Mood swings
- Sensory sensitivity
- Repetitive behaviors
- Difficulty with conversations
- Stress from routine changes

Instead, ask a subtle, **insightful** question that probes the unique cognitive/emotional characteristics of **{diagnosis}**, suitable for follow-up confirmation. Focus on nuance, not basic symptoms.
Ask one question only.
"""

    # Optional: vary tone/depth across followup_index
    tone_variants = [
        "Ask about internal thought patterns or self-reflection habits.",
        "Explore coping mechanisms in unpredictable situations.",
        "Inquire about interpersonal relationships in unfamiliar settings.",
        "Ask whether the individual feels misunderstood or out of sync with peers.",
        "Explore if they rely on certain habits or mental rituals for comfort."
    ]

    # Append extra angle for variety
    prompt = base_prompt + "\n\nFollow this thematic focus: " + tone_variants[followup_index % len(tone_variants)]

    print(f"\n[DEBUG GPT Prompt {followup_index + 1}]:\n{prompt}")

    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful mental health assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content.strip()
