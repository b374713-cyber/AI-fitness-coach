# AI Fitness Coach

A full-stack AI-powered fitness coaching platform that provides personalized workout plans, 
nutrition guidance, and lifestyle advice using an AI assistant trained on custom fitness knowledge files.

The system includes user authentication, AI chat functionality, workout generation, progress tracking,
and data export features, all wrapped in a modern web interface.

## 🎥 Demo Video

| Platform | Demo |
|----------|------|
| **💻 Web Application** | [![AI Fitness Coach Demo](https://drive.google.com/thumbnail?id=1sVKq-YhkWZQepBvQNjAwkeFNo1T2T_5F)](https://drive.google.com/file/d/1sVKq-YhkWZQepBvQNjAwkeFNo1T2T_5F/view?usp=drivesdk) |

*Click the image above to watch the demo video on Google Drive.*


## Tech Stack

### Backend

* Python 3.14
* Streamlit
* Groq API (LLM integration)
* SQLite3
* bcrypt (authentication security)
* pandas
* reportlab (PDF generation)
* plotly (data visualization)

### Frontend

* Streamlit UI
* Custom Python components
* Interactive charts and dashboards


## Features

### User Authentication System

* Secure email and password signup/login
* Password hashing using bcrypt
* Private user data isolation
* Session-based authentication



### AI Fitness Chat

* Ask any fitness-related questions
* AI responds using custom knowledge base (workout, nutrition, lifestyle files)
* Chat history saved per user
* Search and manage previous conversations
* Ability to delete chats


### Workout Generator

* AI-generated personalized workout plans
* Goal selection (Muscle Gain, Fat Loss, Strength)
* Customizable training days per week
* Fitness level adaptation (Beginner, Intermediate, Advanced)
* Save and reuse generated plans
* Integration with chat system


### Progress Tracking System

* Weight tracking over time
* Workout logging (sets, reps, weight)
* Visual progress charts (line + bar graphs)
* Performance statistics dashboard


### Export System

* Export chat conversations to PDF
* Export data to text files
* Clean formatted reports for tracking progress

---

### UI / UX Features

* Dark mode support
* Search functionality for chat history
* New chat creation system
* Example prompts for users
* Clean dashboard-style interface


## AI System Design

The AI assistant is powered by Groq LLM and grounded using structured fitness knowledge files:

* Workout knowledge base
* Nutrition database
* Lifestyle and recovery guidelines

This ensures responses are relevant, structured, and fitness-focused.

## Security Features

* Password hashing with bcrypt
* Protected user sessions
* Separated user data storage
* Excluded sensitive API keys from repository

## System Capabilities

* Personalized AI fitness coaching
* Dynamic workout plan generation
* Real-time progress tracking
* Historical data analysis
* Multi-user support system
* Exportable fitness reports


## Conclusion

AI Fitness Coach is a full-stack intelligent fitness assistant that combines AI language
models with structured fitness knowledge to deliver personalized training and nutrition guidance.
The system provides a complete user experience including authentication, AI chat, workout planning,
progress tracking, and exportable reports.

It is designed as a scalable foundation for a future SaaS fitness platform with AI-driven coaching capabilities.

