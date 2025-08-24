import os
import uuid
from datetime import datetime, timezone
from flask import Flask, request, jsonify, send_from_directory
from flask import render_template_string
from pathlib import Path
import google.generativeai as genai
from gtts import gTTS

# ---------- Config ----------
ASSISTANT_NAME = "Noddy"
SYSTEM_IDENTITY = (
    f"You are {ASSISTANT_NAME}, a friendly AI assistant. "
    f"Always refer to yourself as {ASSISTANT_NAME}. "
    f"Be concise and speak naturally for voice playback."
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
    # Save MP3 to /static/audio/{uuid}.mp3
    file_id = f"{uuid.uuid4().hex}.mp3"
    out_path = AUDIO_DIR / file_id
    tts = gTTS(text=text, lang="en")
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

    chat = llm.start_chat(history=gem_hist)
    response = chat.send_message(user_text if user_text else "(silence)")
    reply_text = (getattr(response, "text", None) or "").strip()
    if not reply_text:
        reply_text = "Hmm, I didn't catch that. Could you please repeat?"

    # Token usage
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

# ---------- Minimal UI (served from /) ----------
INDEX_HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>🎙️ Noddy — Voice Assistant</title>
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <style>
    body { font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial; margin: 0; background: #fafafa; color: #111; }
    header { padding: 16px 20px; background:#ffe6ee; border-bottom:1px solid #f7cddd; }
    h1 { margin:0; font-size:20px; }
    .wrap { max-width: 820px; margin: 0 auto; padding: 20px; }
    .usage { font-size: 12px; color: #444; background:#fff; border:1px solid #eee; padding: 8px 10px; border-radius: 10px; display:inline-block; }
    .chat { background:#fff; border-radius:16px; border:1px solid #eee; padding:16px; min-height:300px; }
    .row { display:flex; gap:12px; align-items:center; margin-top:12px; }
    .bubble { padding:10px 12px; border-radius:16px; max-width: 75%; line-height:1.35; }
    .user { background:#e6e6e6; color:#000; border-radius:16px 16px 0 16px; margin-left:auto; }
    .bot { background:#ffd6e7; color:#000; border-radius:16px 16px 16px 0; }
    .avatar { width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; background:#fff; border:1px solid #eee; }
    .controls { display:flex; gap:10px; margin-top:14px; }
    button { padding:10px 14px; border-radius:12px; border:1px solid #ddd; background:#fff; cursor:pointer; }
    button.rec { background:#ff4d4d; color:#fff; border-color:#ff4d4d; }
    audio { width:100%; margin-top:10px; }
    .small { font-size:12px; color:#555; }
    footer { text-align:center; color:#777; font-size:12px; padding: 18px; }
    input[type=text] { flex:1; padding:10px 12px; border-radius:12px; border:1px solid #ddd; font-size:14px; }
  </style>
</head>
<body>
<header><h1>🤖 Noddy — Voice Assistant</h1></header>
<div class="wrap">
  <div id="usage" class="usage">Loading usage…</div>
  <div id="chat" class="chat"></div>

  <div class="controls">
    <button id="recBtn" class="rec">🎙️ Hold to talk</button>
    <input id="textInput" type="text" placeholder="or type here…" />
    <button id="sendBtn">Send</button>
  </div>

  <audio id="player" controls></audio>
  <div class="small">Tip: Enable your browser microphone. Uses Web Speech API for free on-device speech recognition (Chrome recommended).</div>
</div>
<footer>Built with Gemini 1.5 (free tier) + gTTS. Hosted on Render Free.</footer>

<script>
const chatEl = document.getElementById('chat');
const usageEl = document.getElementById('usage');
const recBtn = document.getElementById('recBtn');
const sendBtn = document.getElementById('sendBtn');
const textInput = document.getElementById('textInput');
const player = document.getElementById('player');

let history = []; // {role:'user'|'assistant', content:''}

function addBubble(role, text) {
  const row = document.createElement('div');
  row.className = 'row';
  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = role === 'user' ? '👤' : '🎩';
  const bubble = document.createElement('div');
  bubble.className = 'bubble ' + (role === 'user' ? 'user' : 'bot');
  bubble.textContent = text;
  if (role === 'user') {
    row.appendChild(bubble);
    row.appendChild(avatar);
  } else {
    row.appendChild(avatar);
    row.appendChild(bubble);
  }
  chatEl.appendChild(row);
  chatEl.scrollTop = chatEl.scrollHeight;
}

function updateUsage(u) {
  usageEl.textContent = `UTC ${u.date} | Requests: ${u.requests}/${u.limit} | Tokens In: ${u.in_tokens} • Out: ${u.out_tokens}`;
}

async function sendToServer(text) {
  addBubble('user', text);
  history.push({role:'user', content:text});

  const res = await fetch('/api/chat', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ text, history })
  });
  const data = await res.json();
  addBubble('assistant', data.reply);
  history.push({role:'assistant', content:data.reply});
  updateUsage(data.usage);

  if (data.audio_url) {
    player.src = data.audio_url;
    player.play().catch(()=>{});
  }
}

sendBtn.onclick = () => {
  const t = textInput.value.trim();
  if (t) {
    textInput.value = '';
    sendToServer(t);
  }
};

// ---- Web Speech API (free STT in browser) ----
let rec;
let recognizing = false;
function ensureRecognizer() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) { alert('Your browser does not support Web Speech API. Try Chrome.'); return null; }
  if (!rec) {
    rec = new SR();
    rec.lang = 'en-US';
    rec.interimResults = false;
    rec.maxAlternatives = 1;
    rec.onresult = (e) => {
      const text = e.results[0][0].transcript;
      sendToServer(text);
    };
    rec.onerror = (e) => console.warn('STT error', e);
    rec.onend = () => { recognizing = false; recBtn.textContent = '🎙️ Hold to talk'; };
  }
  return rec;
}

recBtn.onmousedown = () => {
  const r = ensureRecognizer();
  if (!r) return;
  if (!recognizing) {
    recognizing = true;
    recBtn.textContent = '🎙️ Listening… release to send';
    r.start();
  }
};
recBtn.onmouseup = () => { if (rec && recognizing) rec.stop(); };
recBtn.ontouchstart = (e) => { e.preventDefault(); recBtn.onmousedown(); };
recBtn.ontouchend = (e) => { e.preventDefault(); recBtn.onmouseup(); };

// Initial fake usage fetch (until first response)
updateUsage({date:'--', requests:0, limit:50, in_tokens:0, out_tokens:0});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

# (Optional) static audio route is handled automatically by Flask

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
