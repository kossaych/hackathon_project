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
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
