import React from 'react';

const MODELS = [
    { id: 'meta/llama-3.1-405b-instruct', name: 'Llama 3.1 405B (NVIDIA)' },
    { id: 'google/gemini-2.0-flash-exp:free', name: 'Gemini 2.0 Flash (Free)' },
    { id: 'mistralai/mistral-7b-instruct:free', name: 'Mistral 7B (Free)' },
    { id: 'x-ai/grok-2-vision-1212', name: 'Grok 2 Vision' },
    { id: 'openai/gpt-3.5-turbo', name: 'GPT-3.5 Turbo' },
    { id: 'anthropic/claude-3-haiku', name: 'Claude 3 Haiku' },
];

const SettingsPanel = ({ isOpen, onClose, currentModel, onModelChange }) => {
    if (!isOpen) return null;

    return (
        <div className="absolute top-16 right-4 bg-white p-4 rounded-2xl shadow-xl border border-gray-100 z-50 w-64 animate-in fade-in slide-in-from-top-2">
            <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold text-noddy-text">Settings</h3>
                <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
                        <path fillRule="evenodd" d="M5.47 5.47a.75.75 0 011.06 0L12 10.94l5.47-5.47a.75.75 0 111.06 1.06L13.06 12l5.47 5.47a.75.75 0 11-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 01-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 010-1.06z" clipRule="evenodd" />
                    </svg>
                </button>
            </div>

            <div className="space-y-3">
                <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">AI Model</label>
                    <select
                        value={currentModel}
                        onChange={(e) => onModelChange(e.target.value)}
                        className="w-full p-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-noddy-pink bg-gray-50"
                    >
                        {MODELS.map(model => (
                            <option key={model.id} value={model.id}>{model.name}</option>
                        ))}
                    </select>
                </div>
            </div>
        </div>
    );
};

export default SettingsPanel;
