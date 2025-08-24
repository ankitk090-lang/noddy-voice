from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from TTS.api import TTS
import uuid
import random
import os

app = FastAPI()

# Mount frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Load TTS model
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts")

VOICE_PATH = "voices/your_voice.wav"

# Optional playful interjections
INTERJECTIONS = ["Hehe!", "Yay!", "Ooh!", "Woohoo!", "Hihi!"]

@app.post("/speak")
async def speak(text: str = Form(...)):
    # Prepend Noddy persona description
    noddy_intro = (
        "You are Noddy, a playful adult cartoon girl. "
        "You speak in a fun, kind, and cheerful way, but you are also very wise. "
        "Make your tone light, friendly, and slightly whimsical, "
        "as if you are giving smart advice in a fun way. "
    )
    
    # Occasionally add a playful interjection
    if random.random() < 0.4:  # 40% chance
        interjection = random.choice(INTERJECTIONS)
        text = f"{interjection} {text}"
    
    # Generate TTS
    output_file = f"output_{uuid.uuid4().hex}.wav"
    tts.tts_to_file(text=noddy_intro + text, speaker_wav=VOICE_PATH, file_path=output_file)
    
    return FileResponse(output_file, media_type="audio/wav", filename="noddy.wav")
