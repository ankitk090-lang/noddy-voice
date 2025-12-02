# Noddy AI Assistant 🎀

Noddy is a playful, pastel-themed AI assistant built with React and FastAPI. It features a distinct "adult cartoon" persona, voice interaction (STT/TTS), and support for multiple LLM providers (OpenRouter, NVIDIA Build).

## Features

-   **Chat Interface**: Beautiful, responsive UI with TailwindCSS.
-   **Long-Term Memory (RAG)**: Upload PDF documents to give Noddy context-aware knowledge.
-   **Smart Voice Interaction**: Talk to Noddy naturally with voice-to-text and hear her reply with a custom ElevenLabs voice.
-   **Multi-Model Support**: Switch between powerful LLMs like Llama 3.1 405B (NVIDIA) and others via OpenRouter.
-   **Modern UI**: A beautiful, pastel-themed interface built with React and TailwindCSS.
-   **FastAPI Backend**: Robust Python backend handling vector storage (ChromaDB) and API integrations.

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
    # Note: If you encounter NumPy errors, ensure you have numpy<2 installed:
    # pip install "numpy<2"
    # Install RAG dependencies for document processing
    pip install "unstructured[pdf]" "unstructured[docx]" "unstructured[pptx]" "unstructured[xlsx]" "unstructured[epub]" "unstructured[odt]" "unstructured[rtf]" "unstructured[tsv]" "unstructured[csv]" "unstructured[html]" "unstructured[xml]" "unstructured[json]" "unstructured[md]" "unstructured[rst]" "unstructured[eml]" "unstructured[msg]" "unstructured[org]" "unstructured[txt]" "unstructured[image]" "unstructured[email]" "unstructured[markdown]" "unstructured[text]" "unstructured[all-docs]"
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
