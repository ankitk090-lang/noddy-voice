import { useState } from 'react';

export const useChat = () => {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Hi there! I'm Noddy. How can I brighten your day? ✨" }
    ]);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const sendMessage = async (text, model) => {
        if (!text.trim()) return;

        const newUserMessage = { role: 'user', content: text };
        setMessages(prev => [...prev, newUserMessage]);
        setIsLoading(true);
        setError(null);

        try {
            // Prepare history for backend (exclude initial greeting to avoid context confusion)
            const history = messages
                .filter((_, index) => index > 0) // Skip the first message (local greeting)
                .map(m => ({ role: m.role, content: m.content }));

            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const response = await fetch(`${API_URL}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: text,
                    history: history,
                    model: model
                }),
            });

            if (!response.ok) {
                throw new Error('Failed to get response from Noddy');
            }

            const data = await response.json();

            // Add AI response
            const aiMessage = { role: 'assistant', content: data.response };
            setMessages(prev => [...prev, aiMessage]);

            return { response: data.response, thoughts: data.thoughts };
        } catch (err) {
            console.error(err);
            setError(err.message);
            setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I'm having trouble connecting right now. 😓" }]);
            return null;
        } finally {
            setIsLoading(false);
        }
    };

    return {
        messages,
        setMessages,
        sendMessage,
        isLoading,
        error
    };
};
