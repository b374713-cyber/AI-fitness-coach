# backend/database.py
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "user_data.db")

def get_connection():
    """Get database connection"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize database with all tables"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Conversations table (user-specific)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            messages TEXT NOT NULL
        )
    ''')
    
    # Workout logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            exercise TEXT NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        )
    ''')
    
    # Weight logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weight_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            weight REAL NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_conversation(username, title, messages):
    """Save conversation for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO conversations (username, title, timestamp, messages) VALUES (?, ?, ?, ?)",
        (username, title, datetime.now().isoformat(), json.dumps(messages))
    )
    conn.commit()
    conn.close()

def get_user_conversations(username):
    """Get all conversations for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, title, timestamp FROM conversations WHERE username = ? ORDER BY timestamp DESC",
        (username,)
    )
    results = cursor.fetchall()
    conn.close()
    
    return [{"id": r[0], "title": r[1], "timestamp": r[2]} for r in results]

def get_conversation_by_id(conversation_id, username):
    """Get a specific conversation by ID (with ownership check)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT messages FROM conversations WHERE id = ? AND username = ?",
        (conversation_id, username)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return json.loads(result[0])
    return None

def delete_conversation(conversation_id, username):
    """Delete a conversation (with ownership check)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM conversations WHERE id = ? AND username = ?",
        (conversation_id, username)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    return affected > 0

def search_conversations(username, keyword):
    """Search conversations by keyword for a specific user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id, title, timestamp, messages FROM conversations WHERE username = ? AND messages LIKE ? ORDER BY timestamp DESC",
        (username, f"%{keyword}%")
    )
    results = cursor.fetchall()
    conn.close()
    
    return [{"id": r[0], "title": r[1], "timestamp": r[2], "messages": json.loads(r[3])} for r in results]

# ============================================
# WEIGHT TRACKING FUNCTIONS
# ============================================

def log_weight(username, weight, date=None):
    """Log body weight for a user"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if date is None:
        date = datetime.now().date().isoformat()
    
    # Check if entry exists for this date
    cursor.execute(
        "SELECT id FROM weight_logs WHERE username = ? AND date = ?",
        (username, date)
    )
    existing = cursor.fetchone()
    
    if existing:
        # Update existing entry
        cursor.execute(
            "UPDATE weight_logs SET weight = ? WHERE username = ? AND date = ?",
            (weight, username, date)
        )
    else:
        # Insert new entry
        cursor.execute(
            "INSERT INTO weight_logs (username, date, weight) VALUES (?, ?, ?)",
            (username, date, weight)
        )
    
    conn.commit()
    conn.close()

def get_weight_history(username, days=90):
    """Get weight history for charts (last 90 days by default)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """SELECT date, weight FROM weight_logs 
           WHERE username = ? 
           ORDER BY date DESC LIMIT ?""",
        (username, days)
    )
    results = cursor.fetchall()
    conn.close()
    
    # Return in chronological order
    return [{"date": r[0], "weight": r[1]} for r in reversed(results)]

def delete_weight_entry(username, date):
    """Delete a weight entry"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM weight_logs WHERE username = ? AND date = ?",
        (username, date)
    )
    conn.commit()
    conn.close()

# ============================================
# WORKOUT TRACKING FUNCTIONS
# ============================================

def log_workout_completion(username, exercise_name, sets, reps, weight):
    """Log a completed workout"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO workout_logs (username, date, exercise, sets, reps, weight) 
           VALUES (?, ?, ?, ?, ?, ?)""",
        (username, datetime.now().date().isoformat(), exercise_name, sets, reps, weight)
    )
    conn.commit()
    conn.close()

def get_workout_stats(username, days=30):
    """Get workout statistics for charts"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get workouts per day
    cursor.execute(
        """SELECT date, COUNT(*) as count FROM workout_logs 
           WHERE username = ? AND date >= date('now', ?) 
           GROUP BY date ORDER BY date""",
        (username, f'-{days} days')
    )
    results = cursor.fetchall()
    conn.close()
    
    return [{"date": r[0], "count": r[1]} for r in results]

# Initialize database on import
init_db()