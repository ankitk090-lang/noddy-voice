from fastapi import FastAPI, HTTPException, Response, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import logging
import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
import io

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
MODEL_NAME = "meta/llama-3.1-405b-instruct"

# RAG Configuration
CHROMA_PATH = "chroma_db"
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="noddy_knowledge")
embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

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
    thoughts: list[str] = []

@app.get("/")
def read_root():
    return {"message": "Noddy AI Backend is running"}

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Read PDF
        content = await file.read()
        pdf = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

        # Split text into chunks
        chunk_size = 500
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        # Add to ChromaDB
        ids = [f"{file.filename}_{i}" for i in range(len(chunks))]
        metadatas = [{"source": file.filename} for _ in range(len(chunks))]
        
        # Generate embeddings and add to collection
        collection.add(
            documents=chunks,
            ids=ids,
            metadatas=metadatas
        )
        
        return {"message": f"Successfully processed {file.filename} with {len(chunks)} chunks."}

    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    thoughts = []
    thoughts.append(f"Analyzing user query: '{request.message}'")
    
    current_model = request.model

    # RAG Retrieval
    context = ""
    try:
        thoughts.append("Searching long-term memory (Vector DB)...")
        results = collection.query(
            query_texts=[request.message],
            n_results=3
        )
        if results['documents'] and results['documents'][0]:
            num_results = len(results['documents'][0])
            thoughts.append(f"Found {num_results} relevant memory fragments.")
            context = "\n".join(results['documents'][0])
            logger.info(f"Retrieved context: {context[:100]}...")
            
            # Add source info to thoughts if available
            if results['metadatas'] and results['metadatas'][0]:
                sources = set([m.get('source', 'unknown') for m in results['metadatas'][0]])
                thoughts.append(f"Sources: {', '.join(sources)}")
        else:
            thoughts.append("No relevant memories found.")
            
    except Exception as e:
        logger.error(f"RAG Error: {e}")
        thoughts.append(f"Memory retrieval failed: {str(e)}")

    # Determine Provider
    if "meta/llama" in current_model and "vision" in current_model:
        # NVIDIA Vision Model (Llama 3.2 Vision)
        api_key = os.getenv("NVIDIA_API_KEY")
        api_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        if not api_key:
             # Fallback to OpenRouter if NVIDIA key missing
             logger.warning("NVIDIA API Key missing, falling back to OpenRouter")
             api_key = OPENROUTER_API_KEY
             api_url = OPENROUTER_URL
    elif current_model == "meta/llama-3.1-405b-instruct":
        # NVIDIA Text Model
        api_key = os.getenv("NVIDIA_API_KEY")
        api_url = "https://integrate.api.nvidia.com/v1/chat/completions"
        if not api_key:
             raise HTTPException(status_code=500, detail="NVIDIA API Key not configured")
    else:
        # OpenRouter (Gemini, Claude, GPT, etc.)
        api_key = OPENROUTER_API_KEY
        api_url = OPENROUTER_URL
        if not api_key:
             raise HTTPException(status_code=500, detail="OpenRouter API Key not configured")

    system_prompt = NODDY_PERSONA
    if context:
        thoughts.append("Injecting memory context into system prompt.")
        system_prompt += f"\n\nUse the following context to answer the user's question if relevant:\n{context}"

    messages = [{"role": "system", "content": system_prompt}]
    
    # Append history (limit to last 10 messages)
    messages.extend(request.history[-10:])
    
    # Construct User Message
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
        "model": current_model,
        "messages": messages,
        "max_tokens": 1024
    }

    try:
        thoughts.append(f"Sending request to LLM ({current_model})...")
        logger.info(f"Sending request to {api_url} with model {payload['model']}")
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        
        if "choices" in data and len(data["choices"]) > 0:
            ai_message = data["choices"][0]["message"]["content"]
            thoughts.append("Received response from LLM.")
            return ChatResponse(response=ai_message, thoughts=thoughts)
        else:
            logger.error(f"Unexpected response format: {data}")
            raise HTTPException(status_code=502, detail="Invalid response from LLM provider")

    except requests.exceptions.RequestException as e:
        logger.error(f"Provider API error: {e}")
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
