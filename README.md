# Noddy AI Assistant 🎀

Noddy is a playful, pastel-themed AI assistant built with React and FastAPI. It features a distinct "adult cartoon" persona, voice interaction (STT/TTS), and support for multiple LLM providers (OpenRouter, NVIDIA Build).

## Features

-   **Chat Interface**: Beautiful, responsive UI with TailwindCSS.
-   **Voice Interaction**:
    -   Microphone input (Web Speech API).
    -   High-quality voice output (ElevenLabs).
-   **Multi-Model Support**: Switch between Gemini, Llama 3.1, Mistral, and more.
-   **Persona**: A unique, engaging character that persists across conversations.

## Project Structure

-   `frontend/`: React + Vite application.
-   `backend/`: FastAPI Python server.

## Setup & Installation

### Backend

1.  Navigate to the backend:
    ```bash
    cd backend
    ```
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Create a `.env` file with your API keys (see `.env.example` if available, or use your keys for OPENROUTER_API_KEY, NVIDIA_API_KEY, ELEVENLABS_API_KEY).
5.  Run the server:
    ```bash
    uvicorn main:app --reload
    ```

### Frontend

1.  Navigate to the frontend:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Run the development server:
    ```bash
    npm run dev
    ```

## Deployment

See `deployment_guide.md` for instructions on how to deploy to Render (Backend) and Netlify (Frontend).
