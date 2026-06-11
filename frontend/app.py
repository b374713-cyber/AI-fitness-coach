# frontend/app.py - COMPLETE AI Personal Coach (All Features)

import streamlit as st
from groq import Groq
import random
import os
import json
from datetime import datetime

# Import backend modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import GROQ_API_KEYS
from backend.database import (
    get_user_conversations, save_conversation, delete_conversation,
    search_conversations, get_conversation_by_id
)
from frontend.components.login_ui import show_login_ui

# ============================================
# FILE PATHS
# ============================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="AI Personal Coach",
    page_icon="💪",
    layout="wide"
)

# ============================================
# DARK MODE SETUP
# ============================================

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Apply dark mode CSS
if st.session_state.dark_mode:
    st.markdown("""
        <style>
        .stApp {
            background-color: #1e1e1e;
        }
        .stApp header {
            background-color: #1e1e1e;
        }
        .stChatMessage {
            background-color: #2d2d2d;
        }
        .stMarkdown {
            color: #ffffff;
        }
        .stTextInput > div > div > input {
            background-color: #2d2d2d;
            color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp {
            background-color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)

# ============================================
# LOGIN SYSTEM (Email + Password)
# ============================================

result = show_login_ui()

if result and isinstance(result, tuple) and len(result) == 2:
    user_email, user_name = result
else:
    user_email, user_name = None, None

if not user_email:
    st.stop()

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_conversation_id" not in st.session_state:
    st.session_state.current_conversation_id = None
if "generated_workout" not in st.session_state:
    st.session_state.generated_workout = None

# ============================================
# LOAD KNOWLEDGE BASE
# ============================================

@st.cache_data
def load_knowledge():
    data = ""
    files = [
        os.path.join(BASE_DIR, "backend", "workout.txt"),
        os.path.join(BASE_DIR, "backend", "nutrition.txt"),
        os.path.join(BASE_DIR, "backend", "lifestyle.txt")
    ]
    for file in files:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                data += f"\n\n========== {os.path.basename(file).upper()} ==========\n"
                data += f.read()
    return data

knowledge_base = load_knowledge()

# ============================================
# PDF EXPORT FUNCTION
# ============================================

def export_chat_to_pdf(messages, username, user_email):
    """Export chat to PDF format"""
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib import colors
    from io import BytesIO
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        spaceAfter=30,
        textColor=colors.HexColor('#2ecc71')
    )
    
    story = []
    story.append(Paragraph("💪 AI Personal Coach - Chat Report", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>User:</b> {username} ({user_email})", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph(f"<b>Messages:</b> {len(messages)}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    for msg in messages:
        role = "You" if msg["role"] == "user" else "Coach"
        icon = "❓" if msg["role"] == "user" else "💡"
        story.append(Paragraph(f"<b>{icon} {role}:</b>", styles['Heading4']))
        story.append(Paragraph(msg["content"], styles['Normal']))
        story.append(Spacer(1, 10))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# ============================================
# SIDEBAR - ALL FEATURES
# ============================================

with st.sidebar:
    display_name = user_name if user_name else user_email.split('@')[0]
    st.markdown(f"## 👋 Welcome, **{display_name}**!")
    st.caption(f"📧 {user_email}")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.user_name = None
        st.rerun()
    
    st.markdown("---")
    
    # Dark Mode Toggle
    dark_mode_toggle = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    if dark_mode_toggle != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode_toggle
        st.rerun()
    
    st.markdown("---")
    
    # New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_conversation_id = None
        st.rerun()
    
    st.markdown("---")
    st.markdown("## 📜 Chat History")
    
    # Search bar
    search_term = st.text_input("🔍 Search", placeholder="Search conversations...")
    
    if search_term:
        conversations = search_conversations(user_email, search_term)
        if conversations:
            for conv in conversations:
                if st.button(f"💬 {conv['title'][:35]}...", key=f"search_{conv['id']}"):
                    st.session_state.messages = conv['messages']
                    st.session_state.current_conversation_id = conv['id']
                    st.rerun()
        else:
            st.info("No matching conversations")
    else:
        conversations = get_user_conversations(user_email)
        if conversations:
            for conv in conversations:
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(f"💬 {conv['title'][:30]}...", key=f"conv_{conv['id']}"):
                        loaded = get_conversation_by_id(conv['id'], user_email)
                        if loaded:
                            st.session_state.messages = loaded
                            st.session_state.current_conversation_id = conv['id']
                            st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_{conv['id']}"):
                        if delete_conversation(conv['id'], user_email):
                            st.rerun()
                st.caption(f"📅 {conv['timestamp'][:16]}")
                st.markdown("---")
        else:
            st.info("No saved chats yet. Start a conversation!")
    
    st.markdown("---")
    
    # ============================================
    # EXPORT BUTTONS
    # ============================================
    
    if st.session_state.get("messages") and len(st.session_state.messages) > 0:
        st.markdown("### 📤 Share Conversation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📄 PDF", use_container_width=True, key="pdf_btn"):
                try:
                    with st.spinner("Generating PDF..."):
                        pdf_data = export_chat_to_pdf(
                            st.session_state.messages, 
                            display_name, 
                            user_email
                        )
                        st.download_button(
                            label="Download PDF",
                            data=pdf_data,
                            file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            key="pdf_download"
                        )
                except Exception as e:
                    st.error(f"PDF Error: {e}")
        
        with col2:
            if st.button("📝 Text", use_container_width=True, key="text_btn"):
                text_content = f"""💪 AI Personal Coach - Chat Report
{'='*50}
User: {display_name} ({user_email})
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}

"""
                for msg in st.session_state.messages:
                    role = "You" if msg["role"] == "user" else "Coach"
                    icon = "❓" if msg["role"] == "user" else "💡"
                    text_content += f"\n{icon} {role}: {msg['content']}\n"
                    text_content += "-" * 40 + "\n"
                
                st.download_button(
                    label="Download Text",
                    data=text_content,
                    file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    key="text_download"
                )
        
        st.markdown("---")
    
    # ============================================
    # WORKOUT GENERATOR
    # ============================================
    
    with st.expander("🏋️ Workout Generator", expanded=False):
        st.markdown("### Create Custom Workout Plan")
        
        col1, col2 = st.columns(2)
        
        with col1:
            goal = st.selectbox(
                "🎯 Goal",
                ["Muscle Gain", "Fat Loss", "Strength", "Endurance", "General Fitness"],
                key="workout_goal"
            )
            
            days = st.selectbox(
                "📅 Days per Week",
                [3, 4, 5, 6],
                key="workout_days"
            )
        
        with col2:
            fitness_level = st.selectbox(
                "💪 Fitness Level",
                ["Beginner", "Intermediate", "Advanced"],
                key="fitness_level"
            )
            
            focus_area = st.selectbox(
                "🎯 Focus Area",
                ["Full Body", "Upper Body", "Lower Body", "Core", "Push/Pull/Legs"],
                key="focus_area"
            )
        
        if st.button("✨ Generate Workout Plan", use_container_width=True, key="generate_btn"):
            with st.spinner("Creating your personalized workout plan..."):
                from backend.workout_generator import generate_workout_plan, save_workout
                
                plan = generate_workout_plan(goal, days, fitness_level, focus_area)
                
                if "Error" not in plan:
                    save_workout(user_email, goal, days, fitness_level, focus_area, plan)
                    st.session_state.generated_workout = plan
                    st.success("✅ Workout plan generated and saved!")
                else:
                    st.error(plan)
        
        if st.session_state.get("generated_workout"):
            st.markdown("---")
            st.markdown("### 📋 Your Generated Plan")
            st.markdown(st.session_state.generated_workout)
            
            if st.button("💬 Add to Chat", use_container_width=True):
                chat_message = f"**🎯 Generated Workout Plan**\n\nGoal: {goal}\nDays: {days}/week\nLevel: {fitness_level}\nFocus: {focus_area}\n\n{st.session_state.generated_workout}"
                st.session_state.messages.append({"role": "assistant", "content": chat_message})
                st.rerun()
    
    st.markdown("---")
    
    # ============================================
    # WORKOUT HISTORY
    # ============================================
    
    with st.expander("📋 Saved Workouts", expanded=False):
        from backend.workout_generator import load_user_workouts, delete_workout
        
        workouts = load_user_workouts(user_email)
        
        if workouts:
            for workout in workouts[::-1]:
                with st.container():
                    st.markdown(f"**{workout['goal']} - {workout['days_per_week']} days**")
                    st.caption(f"📅 {workout['timestamp'][:16]} | Level: {workout['fitness_level']}")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        if st.button(f"View", key=f"view_w_{workout['id']}"):
                            st.session_state.generated_workout = workout['plan']
                            st.rerun()
                    with col2:
                        if st.button(f"🗑️", key=f"del_w_{workout['id']}"):
                            delete_workout(user_email, workout['id'])
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("No saved workouts yet. Generate one above!")
    
    st.markdown("---")
    
    # ============================================
    # PROGRESS CHARTS
    # ============================================
    
    with st.expander("📊 Progress Charts", expanded=False):
        from backend.database import get_weight_history, log_weight, get_workout_stats, delete_weight_entry
        from frontend.components.progress_charts import show_progress_charts
        
        show_progress_charts(user_email, get_weight_history, log_weight, get_workout_stats, delete_weight_entry)
    
    st.markdown("---")
    st.markdown("### 📚 Knowledge Base")
    st.markdown("✅ Workout Guide")
    st.markdown("✅ Nutrition Guide")
    st.markdown("✅ Lifestyle Guide")
    
    st.markdown("---")
    st.markdown("### 💡 Example Questions")
    st.markdown("- How to lose weight?")
    st.markdown("- What's a good chest workout?")
    st.markdown("- How much protein do I need?")
    st.markdown("- How to fix my squat form?")

# ============================================
# MAIN CHAT AREA
# ============================================

display_name = user_name if user_name else user_email.split('@')[0]
st.title(f"💪 AI Personal Coach")
st.markdown(f"*Welcome back, {display_name}! Your personal fitness coach*")

# Display messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask your fitness coach..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                current_key = random.choice(GROQ_API_KEYS)
                client = Groq(api_key=current_key)
                
                full_prompt = f"""You are a professional fitness coach. Answer based ONLY on this knowledge:

{knowledge_base}

Question: {prompt}

Answer briefly, helpfully, and with bullet points when appropriate:"""
                
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": full_prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                answer = response.choices[0].message.content
                st.markdown(answer)
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                title = prompt[:40] + "..." if len(prompt) > 40 else prompt
                save_conversation(user_email, title, st.session_state.messages)
                
            except Exception as e:
                st.error(f"Error: {e}")