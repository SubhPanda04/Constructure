import { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { chatAPI, emailAPI } from '../services/api';
import ChatMessage from '../components/ChatMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import EmailCard from '../components/EmailCard';
import ReplyCard from '../components/ReplyCard';

const Dashboard = () => {
    const { user, logout } = useAuth();
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        const sendWelcomeMessage = async () => {
            try {
                const response = await chatAPI.sendMessage('Hello');
                setMessages([
                    {
                        role: 'user',
                        content: 'Hello',
                        timestamp: new Date().toISOString(),
                    },
                    {
                        role: 'assistant',
                        content: response.message,
                        timestamp: response.timestamp,
                    },
                ]);
            } catch (err) {
                console.error('Welcome message error:', err);
            }
        };

        if (user && messages.length === 0) {
            sendWelcomeMessage();
        }
    }, [user]);

    const handleSendMessage = async (e) => {
        e.preventDefault();

        if (!inputMessage.trim() || isLoading) return;

        const userMessage = {
            role: 'user',
            content: inputMessage,
            timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);
        setError(null);

        try {
            const response = await chatAPI.sendMessage(inputMessage);

            // Add AI response
            const aiMessage = {
                role: 'assistant',
                content: response.message,
                timestamp: response.timestamp,
            };
            setMessages((prev) => [...prev, aiMessage]);

            // Handle intents
            if (response.intent?.intent === 'READ_EMAILS') {
                await fetchAndDisplayEmails();
            } else if (response.intent?.intent === 'GENERATE_REPLIES') {
                await fetchAndGenerateReplies();
            }

        } catch (err) {
            console.error('Send message error:', err);
            setError('Failed to send message. Please try again.');
            setMessages((prev) => [
                ...prev,
                {
                    role: 'assistant',
                    content: 'Sorry, I encountered an error processing your request. Please try again.',
                    timestamp: new Date().toISOString(),
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const fetchAndDisplayEmails = async () => {
        setIsLoading(true);
        try {
            const emails = await emailAPI.getRecentEmails();

            if (emails.length === 0) {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: "I couldn't find any recent emails in your inbox.",
                    timestamp: new Date().toISOString()
                }]);
                return;
            }

            // Create a special message component for emails
            const emailMessage = {
                role: 'system',
                type: 'email_list',
                content: emails,
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, emailMessage]);

        } catch (err) {
            console.error('Fetch emails error:', err);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "I had trouble fetching your emails. Please check your connection or try again.",
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const fetchAndGenerateReplies = async () => {
        setIsLoading(true);
        try {
            const emails = await emailAPI.getRecentEmails();

            if (emails.length === 0) {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: "No emails found to generate replies for.",
                    timestamp: new Date().toISOString()
                }]);
                return;
            }

            setMessages(prev => [...prev, {
                role: 'assistant',
                content: `Generating replies for ${emails.length} emails...`,
                timestamp: new Date().toISOString()
            }]);

            // Generate replies sequentially
            const replies = [];
            for (const email of emails) {
                try {
                    const reply = await emailAPI.generateReply(email.id);
                    replies.push(reply);
                } catch (e) {
                    console.error(`Failed to generate reply for ${email.id}`, e);
                }
            }

            if (replies.length > 0) {
                const replyMessage = {
                    role: 'system',
                    type: 'reply_list',
                    content: replies,
                    timestamp: new Date().toISOString()
                };
                setMessages(prev => [...prev, replyMessage]);
            } else {
                throw new Error("Failed to generate any replies");
            }

        } catch (err) {
            console.error('Generate replies error:', err);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "I encountered an error generating replies.",
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleGenerateReply = async (emailId) => {
        setIsLoading(true);
        try {
            const reply = await emailAPI.generateReply(emailId);
            const replyMessage = {
                role: 'system',
                type: 'reply_list',
                content: [reply],
                timestamp: new Date().toISOString()
            };
            setMessages(prev => [...prev, replyMessage]);
        } catch (err) {
            console.error('Generate single reply error:', err);
            alert('Failed to generate reply');
        } finally {
            setIsLoading(false);
        }
    };

    const handleDeleteEmail = async (emailId) => {
        try {
            await emailAPI.deleteEmail(emailId);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "Email deleted successfully.",
                timestamp: new Date().toISOString()
            }]);
        } catch (err) {
            console.error('Delete email error:', err);
            alert('Failed to delete email');
        }
    };

    const handleSendReply = async (emailId, content) => {
        try {
            await emailAPI.sendReply(emailId, content);
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: "Reply sent successfully! 🚀",
                timestamp: new Date().toISOString()
            }]);
        } catch (err) {
            console.error('Send reply error:', err);
            alert('Failed to send reply');
            throw err;
        }
    };

    // Custom renderer for messages including system components
    const renderMessage = (msg, index) => {
        if (msg.type === 'email_list') {
            return (
                <div key={index} className="mb-6 ml-4 max-w-[90%]">
                    <p className="text-sm text-gray-500 mb-2">Here are your recent emails:</p>
                    {msg.content.map(email => (
                        <EmailCard
                            key={email.id}
                            email={email}
                            onGenerateReply={handleGenerateReply}
                            onDelete={handleDeleteEmail}
                        />
                    ))}
                </div>
            );
        }

        if (msg.type === 'reply_list') {
            return (
                <div key={index} className="mb-6 ml-4 max-w-[90%]">
                    <p className="text-sm text-gray-500 mb-2">Here are the generated replies:</p>
                    {msg.content.map((reply, i) => (
                        <ReplyCard
                            key={i}
                            reply={reply}
                            onSend={handleSendReply}
                            onCancel={() => { }}
                        />
                    ))}
                </div>
            );
        }

        return (
            <ChatMessage
                key={index}
                message={msg}
                isUser={msg.role === 'user'}
            />
        );
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            {/* Header */}
            <header className="bg-white shadow-sm border-b border-gray-200 flex-shrink-0">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                            <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                                <svg
                                    className="w-6 h-6 text-white"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                                    />
                                </svg>
                            </div>
                            <h1 className="text-xl font-bold text-gray-900">
                                AI Email Assistant
                            </h1>
                        </div>

                        <div className="flex items-center space-x-4">
                            {user && (
                                <>
                                    <div className="flex items-center space-x-3">
                                        {user.picture && (
                                            <img
                                                src={user.picture}
                                                alt={user.name}
                                                className="w-8 h-8 rounded-full"
                                            />
                                        )}
                                        <div className="hidden sm:block">
                                            <p className="text-sm font-medium text-gray-900">
                                                {user.name}
                                            </p>
                                            <p className="text-xs text-gray-600">{user.email}</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={logout}
                                        className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
                                    >
                                        Logout
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Chat Area */}
            <main className="flex-1 overflow-hidden flex flex-col max-w-4xl w-full mx-auto">
                {/* Messages Container */}
                <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
                    {messages.map((message, index) => renderMessage(message, index))}

                    {isLoading && <LoadingSpinner message="AI is working..." />}

                    {error && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
                            {error}
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div className="border-t border-gray-200 bg-white px-4 py-4 flex-shrink-0">
                    <form onSubmit={handleSendMessage} className="flex space-x-3">
                        <input
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            placeholder="Type your message... (e.g., 'Show my recent emails')"
                            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            disabled={isLoading}
                        />
                        <button
                            type="submit"
                            disabled={isLoading || !inputMessage.trim()}
                            className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            <svg
                                className="w-5 h-5"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
                                />
                            </svg>
                        </button>
                    </form>

                    <p className="text-xs text-gray-500 mt-2 text-center">
                        Try: "Show my recent emails" • "Generate replies" • "Delete email from..."
                    </p>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
