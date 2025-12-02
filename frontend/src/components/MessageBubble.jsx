import React from 'react';

const MessageBubble = ({ message }) => {
    const isUser = message.role === 'user';

    return (
        <div className={`flex w-full mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
            <div
                className={`max-w-[80%] px-5 py-3 rounded-2xl shadow-sm text-sm md:text-base
        ${isUser
                        ? 'bg-noddy-blue text-white rounded-br-none'
                        : 'bg-white text-noddy-text border border-gray-100 rounded-bl-none'
                    }`}
            >
                {message.content}
            </div>
        </div>
    );
};

export default MessageBubble;
