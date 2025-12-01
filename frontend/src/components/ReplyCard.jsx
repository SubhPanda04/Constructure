import { useState } from 'react';

const ReplyCard = ({ reply, onSend, onCancel }) => {
    const [content, setContent] = useState(reply.reply_content);
    const [isSending, setIsSending] = useState(false);
    const [isEditing, setIsEditing] = useState(false);

    const handleSend = async () => {
        if (window.confirm('Ready to send this reply?')) {
            setIsSending(true);
            try {
                await onSend(reply.email_id, content);
            } catch (error) {
                console.error('Send error:', error);
                setIsSending(false);
            }
        }
    };

    return (
        <div className="bg-white border border-green-200 rounded-lg shadow-sm mb-4 overflow-hidden">
            <div className="bg-green-50 px-4 py-2 border-b border-green-100 flex justify-between items-center">
                <span className="text-xs font-semibold text-green-800 flex items-center">
                    <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    AI Draft Reply
                </span>
                <span className="text-xs text-green-600 truncate max-w-[150px]">
                    Re: {reply.original_subject}
                </span>
            </div>

            <div className="p-4">
                {isEditing ? (
                    <textarea
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        className="w-full h-32 p-2 text-sm border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                ) : (
                    <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
                        {content}
                    </p>
                )}

                <div className="mt-4 flex justify-end space-x-3">
                    <button
                        onClick={onCancel}
                        className="text-xs font-medium text-gray-500 hover:text-gray-700"
                    >
                        Discard
                    </button>
                    <button
                        onClick={() => setIsEditing(!isEditing)}
                        className="text-xs font-medium text-gray-600 hover:text-gray-800"
                    >
                        {isEditing ? 'Done' : 'Edit'}
                    </button>
                    <button
                        onClick={handleSend}
                        disabled={isSending}
                        className="px-3 py-1.5 bg-green-600 text-white text-xs font-medium rounded-md hover:bg-green-700 flex items-center disabled:opacity-50"
                    >
                        {isSending ? (
                            <>
                                <svg className="animate-spin -ml-1 mr-2 h-3 w-3 text-white" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Sending...
                            </>
                        ) : (
                            <>
                                Send Reply
                                <svg className="ml-1.5 w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                                </svg>
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ReplyCard;
