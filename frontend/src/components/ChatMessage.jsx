const ChatMessage = ({ message, isUser }) => {
    const formatTime = (timestamp) => {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
            <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${isUser
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
            >
                <div className="flex items-start space-x-2">
                    {!isUser && (
                        <div className="flex-shrink-0 mt-1">
                            <div className="w-6 h-6 bg-primary-600 rounded-full flex items-center justify-center">
                                <svg
                                    className="w-4 h-4 text-white"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                                    />
                                </svg>
                            </div>
                        </div>
                    )}
                    <div className="flex-1">
                        <p className="text-sm whitespace-pre-wrap break-words">
                            {message.content}
                        </p>
                        {message.timestamp && (
                            <p
                                className={`text-xs mt-1 ${isUser ? 'text-primary-100' : 'text-gray-500'
                                    }`}
                            >
                                {formatTime(message.timestamp)}
                            </p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ChatMessage;
