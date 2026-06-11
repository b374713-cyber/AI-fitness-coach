# AI Personal Coach - Complete Version with 3 Files

from groq import Groq
from config import GROQ_API_KEYS
import random
import os

# ============================================
# LOAD ALL 3 FITNESS FILES
# ============================================

data = ""

# List of your 3 files
files = ["workout.txt", "nutrition.txt", "lifestyle.txt"]

print("=" * 60)
print("🤖 AI PERSONAL COACH - LOADING KNOWLEDGE BASE...")
print("=" * 60)

for file in files:
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
            data += f"\n\n========== {file.upper()} ==========\n"
            data += content
        print(f"✅ Loaded: {file}")
    else:
        print(f"❌ WARNING: {file} not found!")

print("=" * 60)
print("🎯 AI PERSONAL COACH IS READY!")
print("📚 Knowledge base: Workout + Nutrition + Lifestyle")
print("💬 Ask me anything about fitness, training, nutrition, or recovery!")
print("⌨️  Type 'quit' to exit")
print("=" * 60)

# ============================================
# INITIALIZE GROQ WITH RANDOM API KEY
# ============================================

current_key = random.choice(GROQ_API_KEYS)
client = Groq(api_key=current_key)

# ============================================
# MAIN CHAT LOOP
# ============================================

while True:
    question = input("\n❓ You: ")
    
    if question.lower() == 'quit':
        print("\n💪 Keep training hard! Stay consistent! Goodbye! 👋")
        break
    
    if question.strip() == "":
        print("💡 Please ask a question!")
        continue
    
    prompt = f"""You are a professional, friendly personal fitness coach. 
Answer based ONLY on the information provided in the fitness guide below.

{data}

Question: {question}

Instructions:
- Answer briefly, helpfully, and in a friendly tone
- Use bullet points when appropriate
- Only use information from the guide above
- If the information isn't in the guide, say "I don't have that information in my fitness guide"
- Be encouraging and positive
- Include specific numbers and examples when available"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7
        )
        print(f"\n💡 Coach: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"\n⚠️ Error: {e}")
        print("🔄 Trying another API key...")
        
        # Try a different key
        current_key = random.choice(GROQ_API_KEYS)
        client = Groq(api_key=current_key)
        
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600,
                temperature=0.7
            )
            print(f"\n💡 Coach: {response.choices[0].message.content}")
        except Exception as e2:
            print(f"⚠️ Still having issues: {e2}")
            print("Please check your API keys in config.py")