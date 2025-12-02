import React, { useState, useEffect, useRef } from 'react';

const ThoughtLogger = ({ thoughts, isThinking }) => {
    const [displayedThoughts, setDisplayedThoughts] = useState([]);
    const [isExpanded, setIsExpanded] = useState(false);
    const scrollRef = useRef(null);

    // Auto-scroll to bottom of thoughts
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [thoughts]);

    // Auto-expand when thinking starts, collapse after a delay when done
    useEffect(() => {
        if (isThinking) {
            setIsExpanded(true);
        } else {
            const timer = setTimeout(() => setIsExpanded(false), 3000);
            return () => clearTimeout(timer);
        }
    }, [isThinking]);

    if (!isThinking && thoughts.length === 0) return null;

    return (
        <div
            className={`fixed bottom-24 right-6 z-40 transition-all duration-300 ease-in-out flex flex-col items-end ${isExpanded ? 'w-80' : 'w-auto'}`}
            onMouseEnter={() => setIsExpanded(true)}
            onMouseLeave={() => !isThinking && setIsExpanded(false)}
        >
            {/* The Bubble Content */}
            {isExpanded && (
                <div className="bg-white p-4 rounded-2xl rounded-br-none shadow-xl border border-noddy-blue/30 mb-2 w-full max-h-60 overflow-hidden flex flex-col animate-in fade-in slide-in-from-bottom-2">
                    <div className="flex items-center gap-2 mb-2 border-b border-gray-100 pb-2">
                        <span className="text-xl">🧠</span>
                        <span className="text-xs font-bold text-noddy-text/50 uppercase tracking-wider">Noddy's Thoughts</span>
                    </div>

                    <div
                        ref={scrollRef}
                        className="overflow-y-auto flex-1 space-y-2 scrollbar-thin scrollbar-thumb-noddy-blue/20"
                    >
                        {thoughts.length === 0 ? (
                            <div className="text-sm text-gray-400 italic animate-pulse">Thinking...</div>
                        ) : (
                            thoughts.map((thought, index) => (
                                <div key={index} className="text-xs text-gray-600 font-medium border-l-2 border-noddy-blue/30 pl-2 py-1">
                                    {thought}
                                </div>
                            ))
                        )}
                        {isThinking && (
                            <div className="flex gap-1 justify-center mt-2 opacity-50">
                                <div className="w-1.5 h-1.5 bg-noddy-blue rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                <div className="w-1.5 h-1.5 bg-noddy-blue rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                <div className="w-1.5 h-1.5 bg-noddy-blue rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* The Trigger Icon (Cloud) */}
            <button
                onClick={() => setIsExpanded(!isExpanded)}
                className={`bg-white p-3 rounded-full shadow-lg border border-noddy-blue/20 hover:scale-110 transition-transform ${isThinking ? 'animate-pulse ring-2 ring-noddy-blue/30' : ''}`}
            >
                <span className="text-2xl">💭</span>
            </button>
        </div>
    );
};

export default ThoughtLogger;
