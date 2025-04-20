from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from ensemble import predict_diagnosis_from_structured
from recommendation import get_recommendation
from nlp import extract_symptoms
from adaptive_routing import route_next_question
from confidence_adjust import adjust_confidence
import csv
import os
from datetime import timedelta
import certifi

# 🔁 Load environment variables
load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ✅ MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, tls=True, tlsCAFile=certifi.where())
db = client["Patient1"]
users_collection = db["users"]

# ✅ JWT setup
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "secret")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(app)

# 🔍 General diagnostic questions
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

# 🔧 Interpret Q1–Q10 Answers
def interpret_q_answer(index, text):
    text = text.lower().strip()
    if any(x in text for x in ["always", "frequently", "daily", "often", "yes", "sure", "absolutely", "i do", "definitely"]):
        return 1
    elif any(x in text for x in ["sometimes", "maybe", "rarely", "depends", "not sure", "occasionally", "at times"]):
        return 0
    return -1

def form_keys():
    return [
        "Gender", "Country", "Occupation", "self_employed", "family_history", "treatment",
        "Growing_Stress", "Changes_Habits", "Mental_Health_History", "Mood_Swings",
        "Coping_Struggles", "Work_Interest", "Social_Weakness", "mental_health_interview"
    ]

# 💬 Chat route for Q1–Q10
@app.route('/chat', methods=['POST'])
@jwt_required()
def chat():
    data = request.get_json()
    message = data["message"]
    index = data.get("question_index", 0)
    responses = data.get("answers", [])

    all_text = " ".join(responses + [message])
    crf_keywords = extract_symptoms(all_text)
    print(f"[DEBUG] Extracted symptoms: {crf_keywords}")

    if index < len(GENERAL_QUESTIONS):
        return jsonify({
            "reply": None,
            "next_question": GENERAL_QUESTIONS[index],
            "question_index": index + 1,
            "followup_count": 0,
            "answers": responses + [message],
            "crf_keywords": crf_keywords,
            "show_result": False
        })

    return jsonify({
        "reply": "Thank you for your responses. Please proceed to final diagnosis.",
        "next_question": None,
        "question_index": 0,
        "followup_count": 0,
        "answers": responses + [message],
        "crf_keywords": crf_keywords,
        "show_result": True
    })

# 📊 Main Prediction Route
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

# 🧠 GPT Follow-up Route (Sequential)
@app.route('/gpt_followup', methods=['POST'])
@jwt_required()
def gpt_followup():
    data = request.get_json()
    current_response = data.get("gpt_response", "")
    all_responses = data.get("gpt_responses", [])
    base_conf = data.get("base_confidence")
    diagnosis = data.get("diagnosis")
    symptoms = data.get("symptoms", [])

    if current_response:
        all_responses.append(current_response)

    adjusted_conf = adjust_confidence(base_conf, all_responses)

    if len(all_responses) < 5:
        next_q = route_next_question(symptoms, diagnosis, base_conf, len(all_responses))
        return jsonify({
            "next_gpt_question": next_q,
            "updated_confidence": adjusted_conf,
            "gpt_responses": all_responses
        })
    else:
        return jsonify({
         "final": True,
         "updated_confidence": adjusted_conf,
         "diagnosis": diagnosis,
         "advice": get_recommendation(diagnosis),
         "resources": ARTICLE_LINKS.get(diagnosis, [])
        })

# 💾 Feedback Logging
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
    hashed = generate_password_hash(password)
    users_collection.insert_one({"email": email, "password": hashed})
    return jsonify({"msg": "Registration successful"}), 201

# 🚀 Start the app
if __name__ == '__main__':
    print("✅ Flask app is starting...")
    app.run(debug=True, use_reloader=False)
