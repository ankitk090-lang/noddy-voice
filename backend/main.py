from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="Noddy AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
# Using a free model as requested, or a reliable fallback
MODEL_NAME = "meta/llama-3.1-405b-instruct"

# Persona Definition
NODDY_PERSONA = """
You are Noddy, a modern, playful, wise, adult-cartoon-persona AI assistant.
Personality traits:
- Playful adult cartoon girl
- Cheerful but wise
- Flirty but respectful
- Answers with warmth and emotional intelligence
- Always stays in character unless performing a technical function

Your goal is to be helpful while maintaining this engaging personality.
"""

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = [] # List of {"role": "user"|"assistant", "content": "..."}
    model: str = "meta/llama-3.1-405b-instruct" # Default model

class ChatResponse(BaseModel):
    response: str

@app.get("/")
def read_root():
    return {"message": "Noddy AI Backend is running"}

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    # Determine Provider
    if request.model == "meta/llama-3.1-405b-instruct":
        api_key = os.getenv("NVIDIA_API_KEY")
        api_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        if not api_key:
             raise HTTPException(status_code=500, detail="NVIDIA API Key not configured")
    else:
        api_key = OPENROUTER_API_KEY
        api_url = OPENROUTER_URL
        if not api_key:
             raise HTTPException(status_code=500, detail="OpenRouter API Key not configured")

    messages = [{"role": "system", "content": NODDY_PERSONA}]
    
    # Append history (limit to last 10 messages to save context/tokens if needed)
    messages.extend(request.history[-10:])
    
    # Append current message
    messages.append({"role": "user", "content": request.message})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    # OpenRouter specific headers
    if "openrouter" in api_url:
        headers["HTTP-Referer"] = "http://localhost:5173"
        headers["X-Title"] = "Noddy AI"

    payload = {
        "model": request.model,
        "messages": messages,
    }

    try:
        logger.info(f"Sending request to {api_url} with model {payload['model']}")
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            ai_message = data["choices"][0]["message"]["content"]
            return ChatResponse(response=ai_message)
        else:
            logger.error(f"Unexpected response format: {data}")
            raise HTTPException(status_code=502, detail="Invalid response from LLM provider")

    except requests.exceptions.RequestException as e:
        logger.error(f"OpenRouter API error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Error details: {e.response.text}")
            raise HTTPException(status_code=502, detail=f"LLM Provider Error: {e.response.text}")
        raise HTTPException(status_code=502, detail=f"Error communicating with LLM provider: {str(e)}")
    except Exception as e:
        logger.error(f"Internal server error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ElevenLabs Configuration
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") # Default voice (Rachel)

class TTSRequest(BaseModel):
    text: str

@app.post("/api/tts")
def tts_endpoint(request: TTSRequest):
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ElevenLabs API Key not configured")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    
    data = {
        "text": request.text,
        "model_id": "eleven_turbo_v2_5",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return Response(content=response.content, media_type="audio/mpeg")
    except requests.exceptions.RequestException as e:
        logger.error(f"ElevenLabs API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
