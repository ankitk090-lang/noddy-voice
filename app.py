import os
import uuid
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template_string
from pathlib import Path
import google.generativeai as genai
from gtts import gTTS

# ---------- Config ----------
ASSISTANT_NAME = "Noddy"
SYSTEM_IDENTITY = (
    f"You are {ASSISTANT_NAME}, a cheerful girl assistant with Noddy’s cartoon personality. "
    f"Always refer to yourself as {ASSISTANT_NAME}. "
    f"Your voice is playful, lively, and distinctly feminine. "
    f"Be concise and natural for voice playback."
)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Please set GEMINI_API_KEY environment variable.")

MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
PORT = int(os.environ.get("PORT", 7860))

genai.configure(api_key=GEMINI_API_KEY)
llm = genai.GenerativeModel(model_name=MODEL_NAME, system_instruction=SYSTEM_IDENTITY)

# ---------- Flask ----------
app = Flask(__name__, static_folder="static", static_url_path="/static")
AUDIO_DIR = Path(app.static_folder) / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# ---------- Usage tracking (UTC daily reset) ----------
USAGE = {
    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    "requests": 0,
    "in_tokens": 0,
    "out_tokens": 0,
}
DAILY_REQUEST_LIMIT = int(os.getenv("DAILY_REQUEST_LIMIT", "50"))

def maybe_reset_usage():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if USAGE["date"] != today:
        USAGE["date"] = today
        USAGE["requests"] = 0
        USAGE["in_tokens"] = 0
        USAGE["out_tokens"] = 0

def usage_panel_md():
    return {
        "date": USAGE["date"],
        "requests": USAGE["requests"],
        "limit": DAILY_REQUEST_LIMIT,
        "in_tokens": USAGE["in_tokens"],
        "out_tokens": USAGE["out_tokens"],
    }

def synthesize_tts(text: str) -> str:
    """Generate Noddy’s female voice (British accent)"""
    file_id = f"{uuid.uuid4().hex}.mp3"
    out_path = AUDIO_DIR / file_id
    # gTTS female-like voice with UK accent
    tts = gTTS(text=text, lang="en", tld="co.uk")
    tts.save(str(out_path))
    return f"/static/audio/{file_id}"

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """
    Body JSON:
      {
        "text": "user message",
        "history": [{"role":"user|assistant", "content":"..."}]   # optional
      }
    """
    maybe_reset_usage()
    if USAGE["requests"] >= DAILY_REQUEST_LIMIT:
        msg = "⚠️ Daily request limit reached for Noddy (Gemini free tier). Please try again tomorrow (UTC)."
        audio_url = synthesize_tts(msg)
        return jsonify({
            "reply": msg,
            "audio_url": audio_url,
            "usage": usage_panel_md()
        })

    data = request.get_json(force=True)
    user_text = (data.get("text") or "").strip()
    history = data.get("history") or []

    # Build Gemini history
    gem_hist = []
    for m in history:
        role = "user" if m.get("role") == "user" else "model"
        content = m.get("content", "")
        if content:
            gem_hist.append({"role": role, "parts": [content]})

    # Chat request
    chat = llm.start_chat(history=gem_hist)
    response = chat.send_message(user_text if user_text else "(silence)")
    reply_text = (getattr(response, "text", None) or "").strip()
    if not reply_text:
        reply_text = "Hmm, I didn’t catch that. Could you please repeat?"

    # Token usage (Gemini usage_metadata)
    usage = getattr(response, "usage_metadata", None)
    in_tok = int(getattr(usage, "prompt_token_count", 0) or 0)
    out_tok = int(getattr(usage, "candidates_token_count", 0) or 0)
    USAGE["requests"] += 1
    USAGE["in_tokens"] += in_tok
    USAGE["out_tokens"] += out_tok

    audio_url = synthesize_tts(reply_text)

    return jsonify({
        "reply": reply_text,
        "audio_url": audio_url,
        "usage": usage_panel_md()
    })

# ---------- Minimal UI ----------
INDEX_HTML = """<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>🎙️ Noddy — Voice Assistant</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
</head>
<body>
  <h1>🤖 Noddy — Voice Assistant</h1>
  <p>Type or speak to Noddy, and she’ll reply in her cheerful girl voice.</p>
  <p>➡️ Visit <code>/api/chat</code> endpoint with JSON {"text":"hello"} for API use.</p>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
