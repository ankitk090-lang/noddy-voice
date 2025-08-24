from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
import os

app = Flask(__name__)

# Configure Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

# Simple HTML front-end (mic + speaker)
html_page = """
<!DOCTYPE html>
<html>
<head>
    <title>Noddy Voice Assistant</title>
</head>
<body style="font-family: Arial; text-align: center; padding: 40px;">
    <h1>🎀 Noddy - Your Chatty Friend 🎀</h1>
    <p>Click the button and talk to Noddy! She'll reply in her cheerful girl voice.</p>

    <button onclick="startChat()">🎤 Talk</button>
    <p id="status"></p>
    <p><b>Noddy says:</b> <span id="reply"></span></p>
    <audio id="audio" controls autoplay></audio>

    <script>
        async function startChat() {
            const text = prompt("Say something to Noddy:");
            if (!text) return;

            document.getElementById("status").innerText = "Thinking...";

            const res = await fetch("/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({message: text})
            });

            const data = await res.json();
            document.getElementById("reply").innerText = data.reply;

            // Get voice
            const audioRes = await fetch("/voice", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({text: data.reply})
            });

            const audioBlob = await audioRes.blob();
            const url = URL.createObjectURL(audioBlob);
            document.getElementById("audio").src = url;

            document.getElementById("status").innerText = "";
        }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(html_page)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    response = model.generate_content(f"Noddy is a cheerful little girl with a cartoon Noddy's personality. Reply playfully:\n\nUser: {user_message}\nNoddy:")
    reply = response.text.strip()
    return jsonify({"reply": reply})

@app.route("/voice", methods=["POST"])
def voice():
    text = request.json.get("text", "")
    from gtts import gTTS
    from io import BytesIO
    tts = gTTS(text=text, lang="en", tld="co.in")  # female voice
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    return app.response_class(mp3_fp.read(), mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
