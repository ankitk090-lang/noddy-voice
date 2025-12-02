import { useState, useEffect, useRef, useCallback } from 'react';

export const useVoice = () => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [voiceEnabled, setVoiceEnabled] = useState(false);
    const recognitionRef = useRef(null);
    const audioRef = useRef(null);

    // Initialize Speech Recognition
    useEffect(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.lang = 'en-US';

            recognition.onstart = () => setIsListening(true);
            recognition.onend = () => setIsListening(false);
            recognition.onresult = (event) => {
                const text = event.results[0][0].transcript;
                setTranscript(text);
            };
            recognition.onerror = (event) => {
                console.error("Speech recognition error", event.error);
                setIsListening(false);
            };

            recognitionRef.current = recognition;
        } else {
            console.warn("Speech Recognition not supported in this browser.");
        }
    }, []);

    const startListening = useCallback(() => {
        if (recognitionRef.current && !isListening) {
            try {
                recognitionRef.current.start();
            } catch (e) {
                console.error("Error starting recognition:", e);
            }
        }
    }, [isListening]);

    const stopListening = useCallback(() => {
        if (recognitionRef.current && isListening) {
            recognitionRef.current.stop();
        }
    }, [isListening]);

    const speak = async (text) => {
        if (!text) return;
        setIsSpeaking(true);

        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const response = await fetch(`${API_URL}/api/tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text }),
            });

            if (!response.ok) throw new Error('TTS request failed');

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);

            if (audioRef.current) {
                audioRef.current.pause();
            }

            const audio = new Audio(url);
            audioRef.current = audio;

            audio.onended = () => {
                setIsSpeaking(false);
                URL.revokeObjectURL(url);
            };

            await audio.play();
        } catch (error) {
            console.error("TTS Error:", error);
            setIsSpeaking(false);
            // Fallback to browser TTS
            const utterance = new SpeechSynthesisUtterance(text);
            const voices = window.speechSynthesis.getVoices();
            const femaleVoice = voices.find(v => v.name.includes('Female') || v.name.includes('Samantha') || v.name.includes('Google US English'));
            if (femaleVoice) utterance.voice = femaleVoice;

            utterance.pitch = 1.1; // Slightly higher pitch for playfulness
            utterance.rate = 1.0;

            utterance.onstart = () => setIsSpeaking(true);
            utterance.onend = () => setIsSpeaking(false);

            window.speechSynthesis.speak(utterance);
        }
    };

    const cancelSpeech = useCallback(() => {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
            setIsSpeaking(false);
        }
    }, []);

    return {
        isListening,
        transcript,
        setTranscript,
        startListening,
        stopListening,
        speak,
        cancelSpeech,
        isSpeaking,
        voiceEnabled,
        setVoiceEnabled
    };
};
