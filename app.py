import gradio as gr
import google.generativeai as genai
import os
from elevenlabs.client import ElevenLabs
import tempfile
import speech_recognition as sr
import traceback
from gtts import gTTS

# Configure APIs
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")
elevenlabs_client = ElevenLabs(api_key="sk_18136ffb1cb2e007b9067179aba66bf60f4207ae87ec9caf")

NODDY_IDENTITY = (
    "You are Noddy, a friendly AI assistant. "
    "Always refer to yourself as Noddy when introducing yourself or answering questions about your name. "
    "Your personality is cheerful, playful, and slightly mischievous like the cartoon Noddy."
)

CUSTOM_VOICE_ID = "1zUSi8LeHs9M2mV8X6YS"  # Replace with your actual ElevenLabs voice ID

def transcribe_audio(audio_filepath):
    if audio_filepath is None:
        return "No audio received"
    
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_filepath) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            recognizer.energy_threshold = 4000
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='en-US')
            return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand the audio. Could you please speak more clearly?"
    except sr.RequestError as e:
        return f"Sorry, there was an error with the speech recognition service: {str(e)}"
    except Exception as e:
        print(f"Audio processing error: {str(e)}")
        return f"An error occurred while processing audio: {str(e)}"

def chat_with_noddy(message, history):
    try:
        formatted_history = []
        for msg in history:
            if isinstance(msg, dict):
                if msg.get("role") == "user":
                    formatted_history.append({"role": "user", "parts": [msg.get("content", "")]})
                elif msg.get("role") == "assistant":
                    formatted_history.append({"role": "model", "parts": [msg.get("content", "")]})
        
        if not formatted_history or formatted_history[0]["parts"][0] != NODDY_IDENTITY:
            formatted_history.insert(0, {"role": "user", "parts": [NODDY_IDENTITY]})

        chat = model.start_chat(history=formatted_history)
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        return f"Sorry, I had trouble processing that. Error: {str(e)}"

def create_audio_response_with_fallback(text):
    """Simple TTS test - just use gTTS for now"""
    print(f"🎯 Creating audio for text: '{text[:100]}...'")
    
    try:
        # Use only gTTS for now to test
        tts = gTTS(text=text, lang='en', slow=False)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            print(f"✅ gTTS file created: {tmp_file.name}")
            
            # Check if file exists and has content
            if os.path.exists(tmp_file.name):
                file_size = os.path.getsize(tmp_file.name)
                print(f"✅ File size: {file_size} bytes")
                if file_size > 0:
                    return tmp_file.name
                else:
                    print("❌ File is empty!")
            else:
                print("❌ File doesn't exist!")
        
        return None
        
    except Exception as e:
        print(f"❌ gTTS Error: {str(e)}")
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return None

def process_conversation(audio_file, chat_history):
    """Main function to process voice conversation"""
    try:
        if audio_file is None:
            return chat_history, None, "Please record some audio first."
        
        user_message = transcribe_audio(audio_file)
        
        if not user_message or "error" in user_message.lower():
            error_msg = "Sorry, I couldn't understand your speech. Please try again."
            return chat_history, None, error_msg
        
        bot_message = chat_with_noddy(user_message, chat_history)
        audio_response = create_audio_response_with_fallback(bot_message)
        
        new_history = chat_history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": bot_message}
        ]
        
        if audio_response:
            status_msg = f"✅ Processed: '{user_message}' - Click ▶️ to play Noddy's response!"
        else:
            status_msg = f"✅ Text processed: '{user_message}' (voice generation failed)"
        
        return new_history, audio_response, status_msg
        
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(f"Error in process_conversation: {traceback.format_exc()}")
        return chat_history, None, error_msg

# Custom CSS
custom_css = """
.chatbot .user {
    background-color: #e6e6e6 !important;
    color: #000000 !important;
    border-radius: 16px 16px 0px 16px !important;
    padding: 10px;
}
.chatbot .bot {
    background-color: #ffd6e7 !important;
    color: #660022 !important;
    border-radius: 16px 16px 16px 0px !important;
    padding: 10px;
}
"""

with gr.Blocks(theme=gr.themes.Soft(), css=custom_css, title="🤖 Noddy Voice Chat") as demo:
    
    gr.Markdown("# 🤖 Noddy Voice Chat")
    gr.Markdown("*Talk to Noddy using your voice! Click the play button ▶️ to hear responses.*")
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                elem_classes=["chatbot"],
                label="Chat History",
                type="messages",
                height=400
            )
            
            status_display = gr.Textbox(
                label="Status",
                value="Ready to chat! Record your message.",
                interactive=False
            )
        
        with gr.Column(scale=1):
            audio_input = gr.Audio(
                type="filepath",
                label="🎤 Speak to Noddy",
                elem_id="audio_input"
            )
            
            audio_output = gr.Audio(
                label="🔊 Noddy's Voice Response",
                autoplay=False,  # Disable autoplay to fix Chrome issues
                interactive=True,
                show_download_button=True
            )
            
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
    
    # State to store chat history - DEFINED HERE!
    chat_state = gr.State([])
    
    # Event handling - NOW chat_state IS DEFINED
    audio_input.change(
        fn=process_conversation,
        inputs=[audio_input, chat_state],
        outputs=[chatbot, audio_output, status_display],
        show_progress=True
    ).then(
        lambda new_history: new_history,
        inputs=[chatbot],
        outputs=[chat_state]
    )
    
    def clear_chat():
        return [], [], "Chat cleared! Ready for new conversation."
    
    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot, chat_state, status_display]
    )
    
    gr.Markdown("""
    ### How to Use:
    1. **Record**: Click microphone and speak your message
    2. **Wait**: Processing takes a few seconds  
    3. **🎵 IMPORTANT**: Click the **play button ▶️** on Noddy's audio response
    4. **Listen**: Enjoy the conversation!

    ### Tips:
    - Chrome blocks autoplay - **manually click play ▶️**
    - You can download the audio file if needed
    - Speak clearly for best results
    """)

if __name__ == "__main__":
    # Start the app
    port = int(os.environ.get("PORT", 10000))
    print(f"Starting Gradio app on 0.0.0.0:{port}")
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True,
        quiet=False
    )
