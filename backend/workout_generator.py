# backend/workout_generator.py
from groq import Groq
from backend.config import GROQ_API_KEYS
import random
import json
from datetime import datetime
import os

# File to save generated workouts
WORKOUTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "generated_workouts.json")

def generate_workout_plan(goal, days_per_week, fitness_level, focus_area):
    """Generate a personalized workout plan using AI"""
    
    current_key = random.choice(GROQ_API_KEYS)
    client = Groq(api_key=current_key)
    
    # Build prompt based on user selections
    prompt = f"""You are an expert personal trainer. Create a {days_per_week}-day workout plan for someone with the following details:

Goal: {goal}
Fitness Level: {fitness_level}
Focus Area: {focus_area}
Days per week: {days_per_week}

Requirements:
- Include specific exercises with sets and reps
- Include warm-up and cool-down recommendations
- Include rest days
- Add progression tips
- Keep it practical and actionable

Format the response with clear sections using bullet points and emojis."""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating workout: {e}"

def save_workout(user_email, goal, days, fitness_level, focus, workout_plan):
    """Save generated workout to history"""
    workouts = load_user_workouts(user_email)
    
    workout_data = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "timestamp": datetime.now().isoformat(),
        "goal": goal,
        "days_per_week": days,
        "fitness_level": fitness_level,
        "focus_area": focus,
        "plan": workout_plan
    }
    
    workouts.append(workout_data)
    
    # Save back to file
    all_workouts = load_all_workouts()
    all_workouts[user_email] = workouts
    
    with open(WORKOUTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_workouts, f, indent=2, ensure_ascii=False)
    
    return workout_data["id"]

def load_user_workouts(user_email):
    """Load all workouts for a specific user"""
    all_workouts = load_all_workouts()
    return all_workouts.get(user_email, [])

def load_all_workouts():
    """Load all workouts from file"""
    if os.path.exists(WORKOUTS_FILE):
        with open(WORKOUTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def delete_workout(user_email, workout_id):
    """Delete a specific workout"""
    workouts = load_user_workouts(user_email)
    workouts = [w for w in workouts if w["id"] != workout_id]
    
    all_workouts = load_all_workouts()
    all_workouts[user_email] = workouts
    
    with open(WORKOUTS_FILE, "w", encoding="utf-8") as f:
        json.dump(all_workouts, f, indent=2, ensure_ascii=False)
    
    return True