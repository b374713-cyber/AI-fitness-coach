# backend/pdf_export.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from io import BytesIO
from datetime import datetime

def export_chat_to_pdf(messages, username, user_email):
    """Export chat conversation to PDF"""
    buffer = BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        spaceAfter=30,
        textColor=colors.HexColor('#2ecc71')
    )
    
    user_style = ParagraphStyle(
        'UserStyle',
        parent=styles['Normal'],
        textColor=colors.HexColor('#3498db'),
        spaceAfter=10,
        leftIndent=20,
        backColor=colors.HexColor('#e8f4fd'),
        borderPadding=10,
        borderRadius=10
    )
    
    coach_style = ParagraphStyle(
        'CoachStyle',
        parent=styles['Normal'],
        textColor=colors.HexColor('#27ae60'),
        spaceAfter=10,
        leftIndent=20,
        backColor=colors.HexColor('#e8f8f0'),
        borderPadding=10,
        borderRadius=10
    )
    
    story = []
    
    # Title
    story.append(Paragraph("💪 AI Personal Coach - Chat Report", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"<b>User:</b> {username} ({user_email})", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph(f"<b>Messages:</b> {len(messages)}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Messages
    for i, msg in enumerate(messages):
        if msg["role"] == "user":
            story.append(Paragraph(f"<b>❓ You:</b>", styles['Heading4']))
            story.append(Paragraph(msg["content"], user_style))
        else:
            story.append(Paragraph(f"<b>💡 Coach:</b>", styles['Heading4']))
            story.append(Paragraph(msg["content"], coach_style))
        story.append(Spacer(1, 10))
    
    doc.build(story)
    buffer.seek(0)
    
    return buffer.getvalue()

def export_single_message(message, role, username):
    """Export a single message as text for sharing"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if role == "user":
        return f"[{timestamp}] ❓ {username}: {message}"
    else:
        return f"[{timestamp}] 💡 AI Coach: {message}"