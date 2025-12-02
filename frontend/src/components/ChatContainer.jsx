import React, { useState, useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import VoiceControls from './VoiceControls';
import SettingsPanel from './SettingsPanel';
import { useChat } from '../hooks/useChat';
import { useVoice } from '../hooks/useVoice';

const ChatContainer = () => {
    const { messages, sendMessage, isLoading } = useChat();
    const {
        isListening,
        transcript,
        setTranscript,
        startListening,
        stopListening,
        speak,
        voiceEnabled,
        setVoiceEnabled
    } = useVoice();

    const [inputText, setInputText] = useState('');
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [currentModel, setCurrentModel] = useState('meta/llama-3.1-405b-instruct');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Update input when voice transcript changes
    useEffect(() => {
        if (transcript) {
            setInputText(transcript);
        }
    }, [transcript]);

    // Handle sending message
    const handleSend = async () => {
        if (!inputText.trim()) return;

        const textToSend = inputText;
        setInputText('');
        setTranscript(''); // Clear voice transcript

        const response = await sendMessage(textToSend, currentModel);

        if (response && voiceEnabled) {
            speak(response);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="flex flex-col h-screen max-w-2xl mx-auto bg-white shadow-xl overflow-hidden md:rounded-xl md:h-[90vh] md:my-[5vh] relative">
            {/* Header */}
            <div className="bg-noddy-pink p-4 flex items-center justify-between shadow-sm z-10">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center text-xl shadow-inner">
                        🎀
                    </div>
                    <div>
                        <h1 className="font-bold text-white text-lg">Noddy AI</h1>
                        <p className="text-xs text-white/80">Always here for you ✨</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setIsSettingsOpen(!isSettingsOpen)}
                        className="p-2 text-white/80 hover:text-white transition-colors"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                            <path fillRule="evenodd" d="M11.078 2.25c-.917 0-1.699.663-1.85 1.567L9.05 5.343c-.2.2-.554.28-.87.207-.618-.146-1.26-.457-1.859-.904-.287-.214-.686-.16-1.006.1l-2.34 1.911c-.34.277-.368.79-.06 1.103l2.586 2.619c.23.232.23.609 0 .841l-2.586 2.619c-.308.313-.28.826.06 1.103l2.34 1.911c.32.26.72.314 1.006.1.599-.447 1.24-.758 1.859-.904.316-.073.67.006.87.207l.178 1.527c.151.903.933 1.566 1.85 1.566h3.044c.917 0 1.699-.663 1.85-1.566l.178-1.527c.2-.2.554-.28.87-.207.618.146 1.26.457 1.859.904.287.214.686.16 1.006-.1l2.34-1.911c.34-.277.368-.79.06-1.103l-2.586-2.619a.599.599 0 010-.841l2.586-2.619c.308-.313.28-.826-.06-1.103l-2.34-1.911a.76.76 0 00-1.006-.1c-.599.447-1.24.758-1.859.904-.316.073-.67-.006-.87-.207l-.178-1.527a1.88 1.88 0 00-1.85-1.566h-3.044zM12 15.75a3.75 3.75 0 100-7.5 3.75 3.75 0 000 7.5z" clipRule="evenodd" />
                        </svg>
                    </button>
                    <div className="text-xs text-white/70 bg-white/20 px-2 py-1 rounded-full">
                        v1.0
                    </div>
                </div>
            </div>

            <SettingsPanel
                isOpen={isSettingsOpen}
                onClose={() => setIsSettingsOpen(false)}
                currentModel={currentModel}
                onModelChange={setCurrentModel}
            />

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 bg-noddy-bg space-y-4">
                {messages.map((msg, index) => (
                    <MessageBubble key={index} message={msg} />
                ))}
                {isLoading && (
                    <div className="flex justify-start mb-4">
                        <div className="bg-white px-4 py-3 rounded-2xl rounded-bl-none shadow-sm border border-gray-100">
                            <div className="flex gap-1">
                                <div className="w-2 h-2 bg-noddy-pink rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                <div className="w-2 h-2 bg-noddy-pink rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                <div className="w-2 h-2 bg-noddy-pink rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-gray-100">
                <div className="flex items-end gap-2">
                    <div className="flex-1 bg-gray-50 rounded-2xl border border-gray-200 focus-within:border-noddy-blue focus-within:ring-1 focus-within:ring-noddy-blue transition-all">
                        <textarea
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                            onKeyDown={handleKeyPress}
                            placeholder="Type a message..."
                            className="w-full bg-transparent border-none focus:ring-0 p-3 max-h-32 resize-none text-sm md:text-base"
                            rows={1}
                        />
                    </div>

                    <VoiceControls
                        isListening={isListening}
                        startListening={startListening}
                        stopListening={stopListening}
                        voiceEnabled={voiceEnabled}
                        setVoiceEnabled={setVoiceEnabled}
                    />

                    <button
                        onClick={handleSend}
                        disabled={!inputText.trim() || isLoading}
                        className="p-3 bg-noddy-pink text-white rounded-full shadow-md hover:bg-red-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                            <path d="M3.478 2.405a.75.75 0 00-.926.94l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94 60.519 60.519 0 0018.445-8.986.75.75 0 000-1.218A60.517 60.517 0 003.478 2.405z" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ChatContainer;
