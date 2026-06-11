# frontend/components/login_ui.py - Email + Password Login

import streamlit as st
import re
from backend.auth import create_user, verify_user

def is_valid_email_format(email):
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def show_login_ui():
    """Display login/signup UI and return (email, name) or (None, None)"""
    
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_email = None
        st.session_state.user_name = None
    
    # If already logged in, return user data
    if st.session_state.logged_in:
        return st.session_state.user_email, st.session_state.user_name
    
    # Show login/signup interface
    st.markdown("## 💪 AI Personal Coach")
    st.markdown("### Welcome! Please login or sign up")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.markdown("#### Login to your account")
        email = st.text_input("Email Address", key="login_email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_btn = st.button("Login", key="login_btn", use_container_width=True)
        
        if login_btn:
            if email and password:
                success, result = verify_user(email, password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.session_state.user_name = result
                    st.rerun()
                    return email, result
                else:
                    st.error(result)
            else:
                st.warning("Please enter both email and password")
    
    with tab2:
        st.markdown("#### Create New Account")
        new_email = st.text_input("Email Address", key="signup_email", placeholder="your@email.com")
        new_name = st.text_input("Display Name (Optional)", key="signup_name", placeholder="How should we call you?")
        new_password = st.text_input("Password", type="password", key="signup_password", placeholder="At least 4 characters")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password", placeholder="Re-enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            signup_btn = st.button("Sign Up", key="signup_btn", use_container_width=True)
        
        if signup_btn:
            if not new_email:
                st.warning("Please enter your email address")
            elif not is_valid_email_format(new_email):
                st.error("Please enter a valid email address (e.g., name@example.com)")
            elif new_password != confirm_password:
                st.error("Passwords don't match")
            elif len(new_password) < 4:
                st.error("Password must be at least 4 characters")
            else:
                success, message = create_user(new_email, new_password, new_name)
                if success:
                    st.success(message + " Please login with your credentials.")
                else:
                    st.error(message)
    
    # Not logged in - return None values
    return None, None