from flask import Flask, request ,jsonify 
from flask import Blueprint, jsonify, request
from models import db, UserProfile
 
import subprocess  
# quiz_questions.py

QUIZ_QUESTIONS = [
    {
        "id": "preferred_language",
        "question": "Which language do you feel most comfortable expressing your thoughts in?",
        "options": ["English", "French", "German", "Other"],
        "mapping": lambda x: x.lower()
    },
    {
        "id": "communication_style",
        "question": "When someone supports you, what do you prefer?",
        "options": [
            "Straight to the point advice",
            "Empathetic and emotional responses",
            "Motivational and encouraging words",
            "Logical and analytical explanations"
        ],
        "mapping": {
            "Straight to the point advice": "direct",
            "Empathetic and emotional responses": "empathetic",
            "Motivational and encouraging words": "motivational",
            "Logical and analytical explanations": "analytical"
        }
    },
    {
        "id": "emotional_expression_level",
        "question": "How easy is it for you to talk about your feelings?",
        "options": [
            "Very hard",
            "Somewhat hard",
            "Somewhat easy",
            "Very easy"
        ],
        "mapping": {
            "Very hard": "low",
            "Somewhat hard": "medium-low",
            "Somewhat easy": "medium-high",
            "Very easy": "high"
        }
    },
    {
        "id": "attention_span_level",
        "question": "Which describes you best?",
        "options": [
            "I lose focus quickly",
            "I can focus for short periods",
            "I stay focused most of the time",
            "I can focus for long periods"
        ],
        "mapping": {
            "I lose focus quickly": "very_short",
            "I can focus for short periods": "short",
            "I stay focused most of the time": "medium",
            "I can focus for long periods": "long"
        }
    },
    {
        "id": "reflection_depth",
        "question": "How deeply do you usually reflect on your thoughts?",
        "options": [
            "I avoid reflecting",
            "I think about things briefly",
            "I analyze my thoughts",
            "I deeply reflect on my emotions"
        ],
        "mapping": {
            "I avoid reflecting": "surface",
            "I think about things briefly": "light",
            "I analyze my thoughts": "moderate",
            "I deeply reflect on my emotions": "deep"
        }
    },
    {
        "id": "support_preference",
        "question": "What kind of support helps you the most?",
        "options": [
            "Just listening",
            "Practical advice",
            "Exercises or techniques",
            "Motivation and encouragement"
        ],
        "mapping": {
            "Just listening": "listening",
            "Practical advice": "advice",
            "Exercises or techniques": "exercises",
            "Motivation and encouragement": "motivation"
        }
    }
]

app = Flask(__name__)  

MAIN_BRANCH = "refs/heads/main" 
@app.route("/update",methods=["POST"])

def update(): 
    data = request.json
    if not data:
        return "No payload", 400

    # Only trigger on pushes to main
    if data.get("ref") != MAIN_BRANCH:
        return "Not main branch, no update triggered", 200

    try:
        backend_path = "/home/hackathonharmonyteam/hackathon_project/backend"
        venv_python = "/home/hackathonharmonyteam/hackathon_project/backend/venv/bin/python3.13"  # adjust to your virtualenv python
        wsgi_file = "/var/www/hackathonharmonyteam_pythonanywhere_com_wsgi.py"

        # Pull latest code
        subprocess.check_call(f"cd {backend_path} && git reset --hard && git pull origin main", shell=True)

        # Install dependencies using virtualenv python
        subprocess.check_call(f"{venv_python} -m pip install -r {backend_path}/requirements.txt", shell=True)

        # Reload app
        subprocess.check_call(f"touch {wsgi_file}", shell=True)

        return "Updated successfully!"
    except subprocess.CalledProcessError as e:
        return f"Update failed: {e}"

@app.route("/")
def index():
    return "Hello World "

@app.route("/api/quiz", methods=["GET"])
def get_quiz():
    """
    Returns quiz questions without internal mappings
    """
    questions = [
        {
            "id": q["id"],
            "question": q["question"],
            "options": q["options"]
        }
        for q in QUIZ_QUESTIONS
    ]

    return jsonify({"questions": questions}), 200

@app.route("/api/quiz/submit", methods=["POST"])
def submit_quiz():
    """
    Expects:
    {
        "user_id": 123,
        "answers": {
            "preferred_language": "English",
            "communication_style": "Empathetic and emotional responses",
            ...
        }
    }
    """
    data = request.get_json()
    user_id = data.get("user_id")
    answers = data.get("answers")

    if not user_id or not answers:
        return jsonify({"error": "Invalid payload"}), 400

    profile_data = {}

    for q in QUIZ_QUESTIONS:
        answer = answers.get(q["id"])
        if not answer:
            continue

        mapping = q["mapping"]

        if callable(mapping):
            profile_data[q["id"]] = mapping(answer)
        else:
            profile_data[q["id"]] = mapping.get(answer)

    # Create & store profile
    user_profile = UserProfile(
        user_id=user_id,
        preferred_language=profile_data.get("preferred_language"),
        communication_style=profile_data.get("communication_style"),
        emotional_expression_level=profile_data.get("emotional_expression_level"),
        attention_span_level=profile_data.get("attention_span_level"),
        reflection_depth=profile_data.get("reflection_depth"),
        support_preference=profile_data.get("support_preference"),
    )

    db.session.add(user_profile)
    db.session.commit()

    return jsonify({
        "message": "Quiz submitted successfully",
        "profile": profile_data
    }), 201



if __name__ == "__main__":
    app.run()
