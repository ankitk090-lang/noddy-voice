import os
import json
import datetime
from flask import Flask, request, jsonify
import google.generativeai as genai

# Flask app
app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Conversation memory (in-memory dict; resets if app restarts)
conversations = {}
DAILY_LIMIT = 50

def count_tokens(text):
    """Naive token count approximation (1 token ≈ 4 chars)."""
    return max(1, len(text) // 4)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id", "default")  # in real app, bind to auth/session
    user_input = data.get("message", "")

    # Initialize user memory if not present
    if user_id not in conversations:
        conversations[user_id] = {
            "history": [],
            "date": datetime.date.today().isoformat(),
            "tokens_used": 0,
            "requests": 0,
        }

    memory = conversations[user_id]

    # Reset daily usage if new day
    today = datetime.date.today().isoformat()
    if memory["date"] != today:
        memory["history"] = []
        memory["date"] = today
        memory["tokens_used"] = 0
        memory["requests"] = 0

    # Check daily quota
    if memory["requests"] >= DAILY_LIMIT:
        return jsonify({
            "reply": "🚫 Noddy is tired for today! Daily request limit reached. Come back tomorrow. 🌙"
        })

    # Build conversation context
    context = "\n".join(
        [f"User: {turn['user']}\nNoddy: {turn['bot']}" for turn in memory["history"]]
    )
    prompt = f"You are Noddy, a cheerful and playful girl with Noddy's cartoon personality.\n" \
             f"Have a fun, friendly chat with the user.\n\n{context}\nUser: {user_input}\nNoddy:"

    # Send to Gemini
    response = model.generate_content(prompt)
    bot_reply = response.text.strip()

    # Update memory
    memory["history"].append({"user": user_input, "bot": bot_reply})
    memory["requests"] += 1
    memory["tokens_used"] += count_tokens(user_input) + count_tokens(bot_reply)

    return jsonify({
        "reply": bot_reply,
        "requests_today": memory["requests"],
        "tokens_used_today": memory["tokens_used"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
