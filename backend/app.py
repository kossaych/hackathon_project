from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
import json
import requests
import subprocess
from sqlalchemy import func
from models import db, UserProfile, ChatSession, ChatMessage, MessageInsight, DailyUserStats

# -------------------------
# Flask App Setup
# -------------------------
app = Flask(__name__)
CORS(app)

# Correct SQLite path
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy
db.init_app(app)

# OpenRouter API Configuration
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# List of models to try in order
MODELS = [
    "nex-agi/deepseek-v3.1-nex-n1:free",
    "mistralai/devstral-2512:free",
    "qwen/qwen-2-7b-instruct:free"
]

MAIN_BRANCH = "refs/heads/main"

# -------------------------
# Quiz Questions
# -------------------------
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
        "options": ["Very hard", "Somewhat hard", "Somewhat easy", "Very easy"],
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

# -------------------------
# Utility Functions
# -------------------------

def openrouter_generate_reply(system_prompt, user_message, max_tokens=500):
    """Generate a reply using OpenRouter API with model fallback"""
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "Mental Health Chatbot"
    }
    
    # Try each model until one works
    for model in MODELS:
        print(f"Trying model: {model}")
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            print(f"Response status for {model}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                if "choices" in data and len(data["choices"]) > 0:
                    reply = data["choices"][0].get("message", {}).get("content", "")
                    
                    if reply:
                        print(f"Success with model: {model}")
                        return reply, model
                    
            else:
                print(f"Failed with {model}: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"Timeout with model: {model}")
            continue
        except Exception as e:
            print(f"Error with model {model}: {str(e)}")
            continue
    
    # If all models failed
    return "I'm having trouble connecting right now. Please try again in a moment.", None


def extract_insights(user_message):
    """Extract insights from user message using OpenRouter"""
    
    system_prompt = """You are an emotional intelligence analyzer. Analyze messages and extract emotional insights.
Always respond with ONLY a valid JSON object, no other text."""

    user_prompt = f"""Analyze this message and return ONLY a JSON object:

Message: "{user_message}"

JSON format:
{{
  "mood": "positive/neutral/negative",
  "emotion": "happy/sad/anxious/stressed/angry/calm/neutral",
  "emotion_intensity": 0.5,
  "attention_level": "low/medium/high",
  "topics": ["topic1"]
}}"""

    response, model = openrouter_generate_reply(system_prompt, user_prompt, max_tokens=200)
    
    try:
        # Try to extract JSON from response
        json_start = response.find('{')
        json_end = response.rfind('}') + 1
        
        if json_start != -1 and json_end > json_start:
            json_str = response[json_start:json_end]
            insights = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["mood", "emotion", "attention_level", "topics"]
            if all(field in insights for field in required_fields):
                return insights
            
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to parse insights: {e}")
        print(f"Response was: {response}")
    
    # Return default insights if parsing fails
    return {
        "mood": "neutral",
        "emotion": "neutral",
        "emotion_intensity": 0.5,
        "attention_level": "medium",
        "topics": ["general"]
    }


def generate_chatbot_reply(user_message, profile, insights):
    """Generate empathetic chatbot reply using OpenRouter"""
    
    # Build profile context
    comm_style = profile.communication_style or 'empathetic'
    support_pref = profile.support_preference or 'listening'
    attention = profile.attention_span_level or 'medium'
    language = profile.preferred_language or 'English'
    
    system_prompt = f"""You are a supportive and empathetic mental health chatbot. Your role is to provide emotional support, active listening, and helpful guidance.

User Profile:
- Communication Style: {comm_style}
- Support Preference: {support_pref}
- Attention Span: {attention}
- Language: {language}

Guidelines:
1. Respond in a warm, supportive, and non-judgmental way
2. Match the user's communication style preference
3. Keep responses concise (2-4 sentences) for attention span
4. Acknowledge their emotions authentically
5. Provide practical support when appropriate
6. Never diagnose or replace professional help
7. Be genuinely caring and present"""

    user_prompt = f"""Current Emotional State:
- Mood: {insights.get('mood', 'neutral')}
- Emotion: {insights.get('emotion', 'neutral')}
- Attention Level: {insights.get('attention_level', 'medium')}

User's Message:
"{user_message}"

Respond with empathy and support:"""

    reply, model = openrouter_generate_reply(system_prompt, user_prompt, max_tokens=300)
    return reply


def store_insights(message_id, insights):
    """Store message insights in database"""
    try:
        topics = insights.get("topics", ["general"])
        topic = topics[0] if isinstance(topics, list) and len(topics) > 0 else "general"
        
        mi = MessageInsight(
            message_id=message_id,
            mood=insights.get("mood", "neutral"),
            emotion=insights.get("emotion", "neutral"),
            emotion_intensity=float(insights.get("emotion_intensity", 0.5)),
            attention_signal=insights.get("attention_level", "medium"),
            distraction=False,
            topic=topic
        )
        db.session.add(mi)
        db.session.commit()
    except Exception as e:
        print(f"Error storing insights: {e}")
        db.session.rollback()


def update_daily_stats(user_id, insights):
    """Update daily statistics for user"""
    try:
        today = date.today()
        stats = DailyUserStats.query.filter_by(user_id=user_id, date=today).first()
        
        mood_val = {"positive": 1, "neutral": 0.5, "negative": 0}.get(insights.get("mood", "neutral"), 0.5)
        attention_val = {"low": 0, "medium": 0.5, "high": 1}.get(insights.get("attention_level", "medium"), 0.5)
        stress_val = 1 if insights.get("emotion") == "stressed" else 0
        
        topics = insights.get("topics", ["general"])
        topic = topics[0] if isinstance(topics, list) and len(topics) > 0 else "general"

        if stats:
            stats.avg_mood = (stats.avg_mood + mood_val) / 2
            stats.attention_score = (stats.attention_score + attention_val) / 2
            stats.stress_level = (stats.stress_level + stress_val) / 2
            stats.dominant_topic = topic
        else:
            stats = DailyUserStats(
                user_id=user_id,
                date=today,
                avg_mood=mood_val,
                attention_score=attention_val,
                stress_level=stress_val,
                dominant_topic=topic
            )
            db.session.add(stats)
        
        db.session.commit()
    except Exception as e:
        print(f"Error updating daily stats: {e}")
        db.session.rollback()

# -------------------------
# Routes
# -------------------------
@app.route("/")
def index():
    return jsonify({
        "message": "Mental Health Chatbot API", 
        "status": "running",
        "version": "1.0",
        "models": MODELS
    }), 200


@app.route("/health")
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


@app.route("/update", methods=["POST"])
def update():
    data = request.json
    if not data:
        return "No payload", 400

    # Only trigger on pushes to main
    if data.get("ref") != MAIN_BRANCH:
        return "Not main branch, no update triggered", 200

    try:
        backend_path = "/home/hackathonharmonyteam/hackathon_project/backend"
        venv_python = "/home/hackathonharmonyteam/hackathon_project/backend/venv/bin/python3.13"
        wsgi_file = "/var/www/hackathonharmonyteam_pythonanywhere_com_wsgi.py"

        subprocess.check_call(f"cd {backend_path} && git reset --hard && git pull origin main", shell=True)
        subprocess.check_call(f"{venv_python} -m pip install -r {backend_path}/requirements.txt", shell=True)
        subprocess.check_call(f"touch {wsgi_file}", shell=True)

        return "Updated successfully!"
    except subprocess.CalledProcessError as e:
        return f"Update failed: {e}"


@app.route("/api/quiz", methods=["GET"])
def get_quiz():
    """Get quiz questions"""
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
    """Submit quiz answers and create user profile"""
    data = request.get_json()
    user_id = data.get("user_id")
    answers = data.get("answers")

    if not user_id or not answers:
        return jsonify({"error": "Invalid payload - missing user_id or answers"}), 400

    try:
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
        
        # Check if profile exists
        user_profile = UserProfile.query.get(user_id)
        if user_profile:
            # Update existing profile
            user_profile.preferred_language = profile_data.get("preferred_language")
            user_profile.communication_style = profile_data.get("communication_style")
            user_profile.attention_span_level = profile_data.get("attention_span_level")
            user_profile.reflection_depth = profile_data.get("reflection_depth")
            user_profile.support_preference = profile_data.get("support_preference")
        else:
            # Create new profile
            user_profile = UserProfile(
                user_id=user_id,
                preferred_language=profile_data.get("preferred_language"),
                communication_style=profile_data.get("communication_style"),
                attention_span_level=profile_data.get("attention_span_level"),
                reflection_depth=profile_data.get("reflection_depth"),
                support_preference=profile_data.get("support_preference")
            )
            db.session.add(user_profile)
        
        db.session.commit()

        return jsonify({
            "message": "Quiz submitted successfully",
            "profile": profile_data
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save profile: {str(e)}"}), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat messages"""
    data = request.get_json()
    user_id = data.get("user_id")
    user_message = data.get("message")

    if not user_id or not user_message:
        return jsonify({"error": "Missing user_id or message"}), 400

    try:
        # Store user message
        user_msg = ChatMessage(user_id=user_id, role="user", content=user_message)
        db.session.add(user_msg)
        db.session.commit()
        
        print(f"Processing message from user {user_id}: {user_message[:50]}...")
        
        # Extract insights using OpenRouter
        insights = extract_insights(user_message)
        print(f"Extracted insights: {insights}")
        
        # Store insights
        store_insights(user_msg.id, insights)
        
        # Get or create user profile
        profile = UserProfile.query.get(user_id)
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)
            db.session.commit()
        
        # Generate chatbot reply using OpenRouter
        reply = generate_chatbot_reply(user_message, profile, insights)
        print(f"Generated reply: {reply[:100]}...")
        
        # Store bot message
        bot_msg = ChatMessage(user_id=user_id, role="bot", content=reply)
        db.session.add(bot_msg)
        
        # Update daily stats
        update_daily_stats(user_id, insights)
        
        db.session.commit()

        return jsonify({
            "reply": reply,
            "insights": insights
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": "An error occurred processing your message",
            "details": str(e)
        }), 500


@app.route("/api/history/<user_id>", methods=["GET"])
def get_chat_history(user_id):
    """Get chat history for a user"""
    try:
        limit = request.args.get("limit", 50, type=int)
        messages = ChatMessage.query.filter_by(user_id=user_id)\
            .order_by(ChatMessage.timestamp.desc())\
            .limit(limit)\
            .all()
        
        history = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in reversed(messages)
        ]
        
        return jsonify({"history": history, "count": len(history)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/stats/<user_id>", methods=["GET"])
def get_user_stats(user_id):
    """Get daily statistics for a user"""
    try:
        days = request.args.get("days", 30, type=int)
        stats = DailyUserStats.query.filter_by(user_id=user_id)\
            .order_by(DailyUserStats.date.desc())\
            .limit(days)\
            .all()
        
        stats_data = [
            {
                "date": stat.date.isoformat(),
                "avg_mood": round(stat.avg_mood, 2),
                "attention_score": round(stat.attention_score, 2),
                "stress_level": round(stat.stress_level, 2),
                "dominant_topic": stat.dominant_topic
            }
            for stat in reversed(stats)
        ]
        
        return jsonify({"stats": stats_data, "count": len(stats_data)}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/profile/<user_id>", methods=["GET"])
def get_user_profile(user_id):
    """Get user profile"""
    try:
        profile = UserProfile.query.get(user_id)
        
        if not profile:
            return jsonify({"error": "Profile not found"}), 404
        
        profile_data = {
            "user_id": profile.user_id,
            "preferred_language": profile.preferred_language,
            "communication_style": profile.communication_style,
            "attention_span_level": profile.attention_span_level,
            "reflection_depth": profile.reflection_depth,
            "support_preference": profile.support_preference,
            "created_at": profile.created_at.isoformat() if profile.created_at else None
        }
        
        return jsonify({"profile": profile_data}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/insights/summary")
def insights_summary():
    start = request.args.get("start")
    end = request.args.get("end")

    query = MessageInsight.query

    if start:
        query = query.filter(MessageInsight.created_at >= datetime.fromisoformat(start))
    if end:
        query = query.filter(MessageInsight.created_at <= datetime.fromisoformat(end))

    # -------- CALENDAR (ALL MOODS PER DAY) --------
    calendar_raw = (
        query.with_entities(
            func.date(MessageInsight.created_at).label("day"),
            MessageInsight.mood,
            func.count().label("count")
        )
        .group_by("day", MessageInsight.mood)
        .all()
    )

    calendar = {}
    for day, mood, count in calendar_raw:
        day = str(day)
        calendar.setdefault(day, {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        })
        calendar[day][mood] = count

    calendar_data = [
        {"date": day, **moods}
        for day, moods in calendar.items()
    ]

    # -------- PIE (MOODS ONLY + PERCENTAGE) --------
    mood_counts = (
        query.with_entities(
            MessageInsight.mood,
            func.count()
        )
        .group_by(MessageInsight.mood)
        .all()
    )

    total = sum(count for _, count in mood_counts)

    pie_data = [
        {
            "mood": mood,
            "count": count,
            "percentage": round((count / total) * 100, 2)
        }
        for mood, count in mood_counts
    ]

    # -------- LINE (EMOTIONS OVER TIME) --------
    evolution = (
        query.with_entities(
            func.date(MessageInsight.created_at).label("day"),
            MessageInsight.emotion,
            func.avg(MessageInsight.emotion_intensity)
        )
        .group_by("day", MessageInsight.emotion)
        .order_by("day")
        .all()
    )

    lines = {}
    for day, emotion, value in evolution:
        lines.setdefault(emotion, []).append({
            "date": str(day),
            "value": round(value, 2)
        })

    return jsonify({
        "calendar": calendar_data,
        "pie": pie_data,
        "lines": lines
    })

# -------------------------
# Create tables & run app
# -------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Database tables created successfully")
        print(f"Using OpenRouter API with models: {', '.join(MODELS)}")
    app.run(debug=True, host="127.0.0.1", port=5000)