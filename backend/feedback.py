# feedback.py
import csv
from datetime import datetime
import os

HEADER = [
    "timestamp",
    *[f"q{i+1}" for i in range(10)],
    *[f"followup{i+1}" for i in range(5)],
    "predicted_label",
    "confidence"
]

def save_feedback(responses, predicted, confidence):
    filepath = 'feedback.csv'

    # Ensure CSV file has header
    file_exists = os.path.isfile(filepath)
    with open(filepath, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(HEADER)

        # Split general vs follow-up
        general = responses[:10]
        followups = responses[10:]
        row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + general + followups
        # Pad to ensure exactly 10 + 5 columns
        row += [""] * (15 - len(general + followups))
        row += [predicted, confidence]

        writer.writerow(row)
