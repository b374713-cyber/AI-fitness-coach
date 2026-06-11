# frontend/components/share_dialog.py
import streamlit as st
from backend.pdf_export import export_chat_to_pdf, export_single_message
from datetime import datetime

def show_share_dialog(messages, username, user_email):
    """Show share dialog with export options"""
    
    st.markdown("### 📤 Share Conversation")
    st.markdown("Choose how you want to share this conversation:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Export as PDF
        if st.button("📄 Export as PDF", use_container_width=True):
            with st.spinner("Generating PDF..."):
                pdf_data = export_chat_to_pdf(messages, username, user_email)
                st.download_button(
                    label="✅ Download PDF",
                    data=pdf_data,
                    file_name=f"coach_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf"
                )
    
    with col2:
        # Export as Text
        if st.button("📝 Export as Text", use_container_width=True):
            text_content = f"""💪 AI Personal Coach - Chat Report
{'='*50}
User: {username} ({user_email})
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}

"""
            for msg in messages:
                if msg["role"] == "user":
                    text_content += f"\n❌ You: {msg['content']}\n"
                else:
                    text_content += f"💡 Coach: {msg['content']}\n"
                text_content += "-" * 40 + "\n"
            
            st.download_button(
                label="✅ Download Text",
                data=text_content,
                file_name=f"coach_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    st.markdown("---")
    
    # Share individual messages
    st.markdown("### 📋 Copy Individual Messages")
    for i, msg in enumerate(messages):
        role_icon = "❓" if msg["role"] == "user" else "💡"
        role_name = "You" if msg["role"] == "user" else "Coach"
        
        col1, col2 = st.columns([5, 1])
        with col1:
            st.text(f"{role_icon} {role_name}: {msg['content'][:100]}...")
        with col2:
            if st.button("📋 Copy", key=f"copy_{i}"):
                st.code(msg["content"], language="text")
                st.success("Copied to clipboard!")