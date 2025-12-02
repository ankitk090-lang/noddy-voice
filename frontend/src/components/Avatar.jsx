import React from 'react';

const Avatar = ({ isListening, isSpeaking, isThinking }) => {
    // Determine state for animations
    const getEyeAnimation = () => {
        if (isThinking) return 'animate-look';
        if (isListening) return 'scale-110'; // Eyes widen when listening
        return 'animate-blink';
    };

    const getMouthAnimation = () => {
        if (isSpeaking) return 'animate-speak';
        return '';
    };

    return (
        <div className="relative w-12 h-12 flex items-center justify-center">
            {/* Floating Container */}
            <div className={`w-full h-full relative animate-float transition-all duration-300 ${isListening ? 'scale-110' : ''}`}>

                {/* Face Shape (Circle) */}
                <div className={`absolute inset-0 rounded-full shadow-inner transition-colors duration-300 ${isListening ? 'bg-noddy-cream' : 'bg-white'
                    }`}></div>

                {/* Bow (The 🎀) */}
                <div className="absolute -top-1 -right-1 text-lg transform rotate-12 z-10">
                    🎀
                </div>

                {/* Face SVG */}
                <svg viewBox="0 0 100 100" className="absolute inset-0 w-full h-full p-2">
                    {/* Eyes Group */}
                    <g className={`transition-transform duration-300 origin-center ${getEyeAnimation()}`}>
                        {/* Left Eye */}
                        <circle cx="35" cy="45" r="6" fill="#4A4A4A" />
                        {/* Right Eye */}
                        <circle cx="65" cy="45" r="6" fill="#4A4A4A" />
                    </g>

                    {/* Mouth Group */}
                    <g className={`transition-transform duration-300 origin-center ${getMouthAnimation()}`}>
                        {/* Mouth Shape changes based on state */}
                        {isSpeaking ? (
                            // Open Mouth (Circle)
                            <circle cx="50" cy="70" r="6" fill="#FFB7B2" />
                        ) : isListening ? (
                            // Listening Mouth (Small 'o')
                            <circle cx="50" cy="70" r="3" fill="#FFB7B2" />
                        ) : (
                            // Idle Smile (Path)
                            <path d="M 40 70 Q 50 75 60 70" stroke="#FFB7B2" strokeWidth="3" fill="none" strokeLinecap="round" />
                        )}
                    </g>

                    {/* Cheeks (Blush) */}
                    <circle cx="25" cy="55" r="4" fill="#FFB7B2" opacity="0.4" />
                    <circle cx="75" cy="55" r="4" fill="#FFB7B2" opacity="0.4" />
                </svg>

                {/* Listening Aura */}
                {isListening && (
                    <div className="absolute -inset-1 bg-noddy-blue rounded-full opacity-20 animate-listen -z-10"></div>
                )}
            </div>
        </div>
    );
};

export default Avatar;
