import { useState } from 'react';
import { emailAPI } from '../services/api';

const EmailCard = ({ email, onGenerateReply, onDelete }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    const handleDelete = async () => {
        if (window.confirm('Are you sure you want to delete this email?')) {
            setIsDeleting(true);
            try {
                await onDelete(email.id);
            } catch (error) {
                console.error('Delete error:', error);
                setIsDeleting(false);
            }
        }
    };

    return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm mb-4 overflow-hidden transition-all hover:shadow-md">
            <div className="p-4">
                <div className="flex justify-between items-start mb-2">
                    <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-semibold text-gray-900 truncate">
                            {email.sender}
                        </h3>
                        <p className="text-xs text-gray-500">{new Date(email.date).toLocaleString()}</p>
                    </div>
                    <div className="flex space-x-2 ml-2">
                        <button
                            onClick={() => setIsExpanded(!isExpanded)}
                            className="text-gray-400 hover:text-gray-600"
                        >
                            <svg className={`w-5 h-5 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                            </svg>
                        </button>
                    </div>
                </div>

                <h4 className="text-sm font-medium text-gray-800 mb-2 truncate">
                    {email.subject}
                </h4>

                <div className="bg-blue-50 rounded-md p-3 mb-3">
                    <p className="text-xs text-blue-800 font-medium mb-1">AI Summary:</p>
                    <p className="text-sm text-gray-700 leading-relaxed">
                        {email.summary}
                    </p>
                </div>

                {isExpanded && (
                    <div className="mt-4 flex justify-end space-x-3 border-t border-gray-100 pt-3">
                        <button
                            onClick={handleDelete}
                            disabled={isDeleting}
                            className="text-xs font-medium text-red-600 hover:text-red-800 flex items-center"
                        >
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                            {isDeleting ? 'Deleting...' : 'Delete'}
                        </button>
                        <button
                            onClick={() => onGenerateReply(email.id)}
                            className="text-xs font-medium text-primary-600 hover:text-primary-800 flex items-center"
                        >
                            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                            </svg>
                            Generate Reply
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default EmailCard;
