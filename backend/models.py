# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    user_id = db.Column(db.Integer, primary_key=True)
    preferred_language = db.Column(db.String(10))
    communication_style = db.Column(db.String(50)) 
    attention_span_level = db.Column(db.String(50))
    reflection_depth = db.Column(db.String(50)) 
    support_preference = db.Column(db.String(50)) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatSession(db.Model):
    __tablename__ = "chat_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)



class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, index=True)
    role = db.Column(db.String(10))  # "user" | "bot"
    content = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MessageInsight(db.Model):
    __tablename__ = "message_insights"

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer)

    mood = db.Column(db.String(20))               # positive | neutral | negative
    emotion = db.Column(db.String(50))            # stress, calm, frustration
    emotion_intensity = db.Column(db.Float)       # 0.0 → 1.0

    attention_signal = db.Column(db.String(20))   # low | medium | high
    distraction = db.Column(db.Boolean)

    topic = db.Column(db.String(50))               # focus, work, motivation

    created_at = db.Column(db.DateTime, default=datetime.utcnow)





class DailyUserStats(db.Model):
    __tablename__ = "daily_user_stats"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    date = db.Column(db.Date)

    avg_mood = db.Column(db.Float)
    attention_score = db.Column(db.Float)
    stress_level = db.Column(db.Float)

    dominant_topic = db.Column(db.String(50))
