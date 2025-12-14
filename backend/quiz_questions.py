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
