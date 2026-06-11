# backend/auth.py - Email + Password Authentication
import hashlib
import json
import os
import re
from datetime import datetime

# User data file
USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "users.json")

def hash_password(password):
    """Hash a password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def load_users():
    """Load all users from JSON file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def create_user(email, password, name=""):
    """Create a new user with email"""
    users = load_users()
    
    # Check if email already exists
    if email in users:
        return False, "Email already registered"
    
    # Validate email
    if not is_valid_email(email):
        return False, "Please enter a valid email address"
    
    # Validate password
    if len(password) < 4:
        return False, "Password must be at least 4 characters"
    
    # Extract name from email if not provided
    if not name:
        name = email.split('@')[0]
    
    users[email] = {
        "email": email,
        "name": name,
        "password": hash_password(password),
        "created_at": datetime.now().isoformat(),
        "settings": {
            "dark_mode": False,
            "default_goal": "Muscle Gain"
        }
    }
    save_users(users)
    return True, "Account created successfully!"

def verify_user(email, password):
    """Verify user credentials by email"""
    users = load_users()
    
    if email not in users:
        return False, "Email not found. Please sign up first."
    
    if users[email]["password"] != hash_password(password):
        return False, "Incorrect password"
    
    return True, users[email]["name"]

def get_user_by_email(email):
    """Get user data by email"""
    users = load_users()
    return users.get(email)

def get_user_settings(email):
    """Get user settings"""
    users = load_users()
    if email in users:
        return users[email].get("settings", {})
    return {}

def update_user_settings(email, settings):
    """Update user settings"""
    users = load_users()
    if email in users:
        users[email]["settings"] = settings
        save_users(users)
        return True
    return False

def get_all_users():
    """Get all users (for admin)"""
    users = load_users()
    return [{"email": u["email"], "name": u["name"], "created_at": u["created_at"]} for u in users.values()]