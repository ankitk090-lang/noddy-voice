import gradio as gr
import google.generativeai as genai
import os
from elevenlabs.client import ElevenLabs
import tempfile
import speech_recognition as sr
import traceback

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# Configure ElevenLabs API
elevenlabs_client = ElevenLabs(api_key="sk_18136ffb1cb2e007b9067179aba66bf60f4207ae87ec9caf")

# Noddy's System Identity
NODDY_IDENTITY = (
    "You are Noddy, a friendly AI assistant. "
    "Always refer to yourself as Noddy when introducing yourself or answering questions about your name. "
    "Your personality is cheerful, playful, and slightly mischievous like the cartoon Noddy."
)

# Your custom ElevenLabs voice ID (replace with your voice ID)
CUSTOM_VOICE_ID = "1zUSi8LeHs9M2mV8X6YS"  # Replace this with your actual voice ID

def transcribe_audio(audio_filepath):
    """Convert audio to text using speech recognition"""
    if audio_filepath is None:
        return "No audio received"
    
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_filepath) as source:
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand the audio. Could you please speak more clearly?"
    except sr.RequestError as e:
        return f"Sorry, there was an error with the speech recognition service: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def chat_with_noddy(message, history):
    """Get response from Gemini API"""
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
def create_elevenlabs_audio(text):
    """Convert text to audio using ElevenLabs API with debug logging"""
    try:
        print(f"🔍 Debug - Text to convert: {text[:50]}...")
        
        # Check if API key is loaded
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            print("❌ Error: ELEVENLABS_API_KEY not found in environment!")
            return None
        
        print(f"✅ API Key loaded: {api_key[:10]}...")
        print(f"✅ Voice ID: {CUSTOM_VOICE_ID}")
        
        # Make API call
        audio = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=CUSTOM_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )
        
        print("✅ ElevenLabs API call successful!")
        
        # Save audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            for chunk in audio:
                if chunk:
                    tmp_file.write(chunk)
            print(f"✅ Audio file created: {tmp_file.name}")
            return tmp_file.name
            
    except Exception as e:
        print(f"❌ ElevenLabs Error: {str(e)}")
        print(f"❌ Full error: {traceback.format_exc()}")
        return None
from gtts import gTTS

def create_audio_response_with_fallback(text):
    """Simple TTS test - just use gTTS for now"""
    print(f"🎯 Creating audio for text: '{text[:100]}...'")
    
    try:
        # Use only gTTS for now to test
        from gtts import gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            print(f"✅ gTTS file created: {tmp_file.name}")
            
            # Check if file exists and has content
            import os
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


'''def create_audio_response_with_fallback(text):
    """Try ElevenLabs first, fallback to gTTS if it fails"""
    
    # Try ElevenLabs first
    audio_file = create_elevenlabs_audio(text)
    if audio_file:
        return audio_file
    
    # Fallback to gTTS
    print("🔄 Falling back to gTTS...")
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            tts.save(tmp_file.name)
            print("✅ gTTS fallback successful!")
            return tmp_file.name
    except Exception as e:
        print(f"❌ gTTS fallback also failed: {str(e)}")
        return None'''

# Update your process_conversation function to use the fallback:
# Replace this line:
# audio_response = create_elevenlabs_audio(bot_message)
# With this:
#audio_response = create_audio_response_with_fallback(bot_message)

'''def create_elevenlabs_audio(text):
    """Convert text to audio using ElevenLabs API"""
    try:
        # Generate audio using ElevenLabs
        audio = elevenlabs_client.text_to_speech.convert(
            text=text,
            voice_id=CUSTOM_VOICE_ID,  # Your custom voice
            model_id="eleven_multilingual_v2",  # High quality model
            output_format="mp3_44100_128"
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
            # Write the audio bytes to file
            for chunk in audio:
                if chunk:
                    tmp_file.write(chunk)
            return tmp_file.name
            
    except Exception as e:
        print(f"ElevenLabs Error: {str(e)}")
        return None'''
with gr.Column(scale=1):
    audio_input = gr.Audio(
        type="filepath",
        label="🎤 Speak to Noddy",
        elem_id="audio_input"
    )
    
    audio_output = gr.Audio(
        label="🔊 Noddy's Voice Response",
        autoplay=False,
        interactive=True,
        show_download_button=True
    )
    
    # Add a play reminder
    play_reminder = gr.Markdown(
        "💡 **After Noddy responds, click the ▶️ play button above to hear the voice!**",
        visible=False
    )
    
    clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")

# Update your process_conversation to show the reminder
def process_conversation(audio_file, chat_history):
    # ... existing code ...
    
    if audio_response:
        reminder_visible = True  # Show play reminder
        status_msg = f"✅ Processed: '{user_message}' - Click ▶️ to play Noddy's response!"
    else:
        reminder_visible = False
        status_msg = f"✅ Text processed: '{user_message}' (voice generation failed)"
    
    return new_history, audio_response, status_msg, reminder_visible

# Update the event handler
audio_input.change(
    fn=process_conversation,
    inputs=[audio_input, chat_state],
    outputs=[chatbot, audio_output, status_display, play_reminder],
    show_progress=True
).then(
    lambda new_history: new_history,
    inputs=[chatbot],
    outputs=[chat_state]
)


def process_conversation(audio_file, chat_history):
    """Main function to process voice conversation"""
    try:
        if audio_file is None:
            return chat_history, None, "Please record some audio first."
        
        # Step 1: Speech-to-text
        user_message = transcribe_audio(audio_file)
        
        if not user_message or "error" in user_message.lower():
            error_msg = "Sorry, I couldn't understand your speech. Please try again."
            return chat_history, None, error_msg
        
        # Step 2: Get Noddy's response
        bot_message = chat_with_noddy(user_message, chat_history)
        
        # Step 3: Create audio response with ElevenLabs
        audio_response = create_elevenlabs_audio(bot_message)
        
        # Step 4: Update chat history
        new_history = chat_history + [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": bot_message}
        ]
        
        return new_history, audio_response, f"✅ Processed: '{user_message[:50]}...'" if len(user_message) > 50 else f"✅ Processed: '{user_message}'"
        
    except Exception as e:
        error_msg = f"An error occurred: {str(e)}"
        print(f"Error in process_conversation: {traceback.format_exc()}")
        return chat_history, None, error_msg

# Custom CSS for better UI
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

# Create Gradio Interface
with gr.Blocks(theme=gr.themes.Soft(), css=custom_css, title="🤖 Noddy Voice Chat") as demo:
    
    gr.Markdown("# 🤖 Noddy Voice Chat with ElevenLabs")
    gr.Markdown("*Talk to Noddy using your voice! Powered by your custom ElevenLabs voice.*")
    
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
                value="Ready to chat with your custom voice! Record your message.",
                interactive=False
            )
        
        with gr.Column(scale=1):
            audio_input = gr.Audio(
                type="filepath",
                label="🎤 Speak to Noddy",
                elem_id="audio_input"
            )
            
            audio_output = gr.Audio(
                label="🔊 Noddy's Custom Voice Response",
                autoplay=True
            )
            
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
    
    chat_state = gr.State([])
    
    # Event handling
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
        return [], [], "Chat cleared! Ready for new conversation with custom voice."
    
    clear_btn.click(
        fn=clear_chat,
        outputs=[chatbot, chat_state, status_display]
    )
    
    gr.Markdown("""
    ### Custom ElevenLabs Voice Features:
    - **High Quality**: Using ElevenLabs Multilingual v2 model
    - **Custom Voice**: Your downloaded ElevenLabs voice
    - **Low Latency**: Fast response times
    - **Emotional Expression**: Natural intonation and emotion
    
    ### How to Use:
    1. **Record**: Click microphone and speak
    2. **Process**: Wait for Noddy to respond with your custom voice
    3. **Listen**: Enjoy the natural-sounding conversation
    """)
    
    gr.Markdown("<small>💡 Powered by Google Gemini 1.5 + ElevenLabs Custom Voice</small>")

if __name__ == "__main__":
    demo.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        show_error=True
    )

