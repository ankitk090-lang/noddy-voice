import { useState, useEffect, useRef, useCallback } from 'react';

export const useVoice = (onResult) => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [isSpeaking, setIsSpeaking] = useState(false);
    const [voiceEnabled, setVoiceEnabled] = useState(true); // Default to true
    const recognitionRef = useRef(null);
    const audioRef = useRef(null);
    const onResultRef = useRef(onResult);

    // Update ref when onResult changes
    useEffect(() => {
        onResultRef.current = onResult;
    }, [onResult]);

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
                if (onResultRef.current) {
                    onResultRef.current(text);
                }
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
        console.log("Attempting to speak:", text); // Debug log
        if (!text) return;
        setIsSpeaking(true);

        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            console.log("Calling TTS API:", `${API_URL}/api/tts`); // Debug log
            const response = await fetch(`${API_URL}/api/tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text }),
            });

            if (!response.ok) throw new Error('TTS request failed');

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            console.log("TTS Audio URL created:", url); // Debug log

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
            console.log("Audio playing..."); // Debug log
        } catch (error) {
            console.error("TTS Error:", error);
            console.log("Falling back to browser TTS"); // Debug log
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
