import React from 'react';
import ReactMarkdown from 'react-markdown';

const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';

    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 shadow-sm ${isUser
                        ? 'bg-noddy-blue text-white rounded-br-none'
                        : 'bg-white text-noddy-text rounded-bl-none border border-gray-100'
                    }`}
            >
                <div className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
            </div>
        </div>
    );
};

export default MessageBubble;
