from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from ensemble import predict_diagnosis, predict_diagnosis_from_structured
from recommendation import get_recommendation
from adaptive_routing import route_next_question
from nlp import extract_symptoms
import csv
import os
from datetime import timedelta

# 🔁 Load .env variables
load_dotenv()
app = Flask(__name__)
CORS(app)

# ✅ MongoDB setup
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
client = MongoClient(app.config["MONGO_URI"])
db = client["Patient1"]
users_collection = db["users"]

# ✅ JWT setup
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# 🔍 General Diagnosis Questions
GENERAL_QUESTIONS = [
    "How often do you find yourself worrying excessively?",
    "Do you feel uncomfortable or anxious in social situations?",
    "Do you find it difficult to concentrate on daily tasks?",
    "Have your sleeping patterns changed or become irregular?",
    "Have you noticed sudden changes in mood or behavior?",
    "Do you find it difficult to express or identify your emotions?",
    "Do you feel the urge to perform repetitive actions or rituals?",
    "Do you find it hard to start or maintain conversations?",
    "Are you very sensitive to sounds, lights, or textures?",
    "Do changes in your routine cause you significant stress?"
]

CONFIDENCE_THRESHOLD = 85
MAX_FOLLOWUPS = 5

ARTICLE_LINKS = {
    "Anxiety": [
        "https://www.nimh.nih.gov/health/topics/anxiety-disorders",
        "https://www.helpguide.org/articles/anxiety/anxiety-disorders-and-anxiety-attacks.htm"
    ],
    "OCD": [
        "https://iocdf.org/about-ocd/",
        "https://www.nimh.nih.gov/health/topics/obsessive-compulsive-disorder-ocd"
    ],
    "Autism": [
        "https://www.cdc.gov/ncbddd/autism/index.html",
        "https://www.autismspeaks.org/what-autism"
    ]
}

# 🔧 Q1–Q10 Interpretation
def interpret_q_answer(index, text):
    text = text.lower()
    if any(x in text for x in ["always", "frequently", "daily", "every day", "often", "all the time"]):
        return 1
    elif any(x in text for x in ["sometimes", "occasionally", "not often", "rarely"]):
        return 0
    return -1

# 📥 Feedback Storage
def save_structured_feedback(responses, diagnosis, confidence, extracted_keywords):
    folder = "data"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "feedback.csv")

    padded = responses[:15] + [""] * (15 - len(responses))
    keyword_str = ", ".join(extracted_keywords or [])
    row = padded + [diagnosis, confidence, keyword_str]

    headers = [f"Q{i+1}" for i in range(10)] + [f"Followup{i+1}" for i in range(5)] + [
        "Diagnosis", "Confidence", "CRF Keywords"
    ]

    file_exists = os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)

# 📌 Static Field Order
def form_keys():
    return [
        "Gender", "Country", "Occupation", "self_employed", "family_history", "treatment",
        "Growing_Stress", "Changes_Habits", "Mental_Health_History", "Mood_Swings",
        "Coping_Struggles", "Work_Interest", "Social_Weakness", "mental_health_interview"
    ]

# 💬 Chat Diagnosis (free text)
@app.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json()
    message = data['message']
    index = data.get('question_index', 0)
    followup_count = data.get('followup_count', 0)
    responses = data.get('answers', [])

    # Combine all text responses for CRF symptom extraction
    all_text = " ".join(responses + [message])
    all_symptoms = extract_symptoms(all_text)
    print(f"[DEBUG] Extracted symptoms: {all_symptoms}")

    # Still asking general diagnostic questions (Q1–Q10)
    if index < len(GENERAL_QUESTIONS):
        return jsonify({
            "reply": None,
            "next_question": GENERAL_QUESTIONS[index],
            "question_index": index + 1,
            "followup_count": 0,
            "answers": responses + [message]
        })

    # If Q1–Q10 are done, we don’t predict yet — wait for `/predict`
    return jsonify({
        "reply": "Thank you for your responses. Please proceed to submit for final diagnosis.",
        "next_question": None,
        "question_index": 0,
        "followup_count": 0,
        "answers": responses + [message],
        "show_result": False,
        "crf_keywords": all_symptoms  # frontend can optionally collect and forward to /predict
    })


    if len(all_symptoms) < 3 or message.lower() in ["ok", "i don't know", "maybe", "not sure"]:
        confidence = min(confidence, 60)

    if confidence < CONFIDENCE_THRESHOLD and followup_count < MAX_FOLLOWUPS:
        next_q = route_next_question(all_symptoms, diagnosis, confidence)
        return jsonify({
            "reply": None,
            "next_question": next_q,
            "question_index": index,
            "followup_count": followup_count + 1,
            "answers": responses + [message]
        })

    if confidence < CONFIDENCE_THRESHOLD:
        return jsonify({
            "reply": "The current responses are inconclusive for a confident diagnosis.\nWe recommend seeking professional medical advice.",
            "next_question": None,
            "question_index": 0,
            "followup_count": 0,
            "show_result": True
        })

    save_structured_feedback(responses + [message], diagnosis, confidence, all_symptoms)
    advice = get_recommendation(diagnosis)
    articles = ARTICLE_LINKS.get(diagnosis, [])
    reply = f"Likely condition: {diagnosis} ({confidence}%)\nRecommendation: {advice}"

    if articles:
        reply += "\n\n🔗 Helpful Reading:\n" + "\n".join(articles)

    return jsonify({
        "reply": reply,
        "next_question": None,
        "question_index": 0,
        "followup_count": 0,
        "show_result": True
    })

# 📊 Structured Prediction (form + interpreted chat)
@app.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    data = request.get_json()
    form = data.get("form", {})
    q_raw_answers = data.get("answers", [])

    structured_qs = {f"Q{i+1}": interpret_q_answer(i, q_raw_answers[i]) for i in range(10)}
    input_data = {**form, **structured_qs}

    diagnosis, confidence = predict_diagnosis_from_structured(input_data)
    advice = get_recommendation(diagnosis)

    return jsonify({
        "prediction": diagnosis,
        "confidence": confidence,
        "advice": advice
    })

# 🔑 Login
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = users_collection.find_one({"email": email})
    if user and check_password_hash(user["password"], password):
        token = create_access_token(identity=email)
        return jsonify(access_token=token), 200
    return jsonify({"msg": "Invalid credentials"}), 401

# 📝 Register
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if users_collection.find_one({"email": email}):
        return jsonify({"msg": "User already exists"}), 409

    hashed_password = generate_password_hash(password)
    users_collection.insert_one({"email": email, "password": hashed_password})
    return jsonify({"msg": "Registration successful"}), 201

# ✅ Feedback Endpoint for Structured Form
@app.route('/log_feedback', methods=['POST'])
@jwt_required()
def log_feedback():
    data = request.get_json()
    form = data.get("form", {})
    q_answers = data.get("answers", [])
    diagnosis = data.get("diagnosis")
    confidence = data.get("confidence")
    symptoms = data.get("symptoms", [])

    folder = "data"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "feedback.csv")

    structured_qs = {f"Q{i+1}": interpret_q_answer(i, q_answers[i]) for i in range(10)}
    row = [form.get(k, "") for k in form_keys()] + list(structured_qs.values()) + [diagnosis, confidence, ", ".join(symptoms)]
    headers = form_keys() + [f"Q{i+1}" for i in range(10)] + ["Diagnosis", "Confidence", "CRF Keywords"]

    file_exists = os.path.isfile(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)

    return jsonify({"msg": "Feedback saved"}), 200

# 🚀 Run Flask App
if __name__ == '__main__':
    print("✅ Flask app is starting...")
    app.run(debug=True)
