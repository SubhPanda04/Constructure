import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
    const { user, logout } = useAuth();

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b border-gray-200">
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

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">
                        Welcome, {user?.name?.split(' ')[0]}! 👋
                    </h2>
                    <p className="text-gray-600 mb-6">
                        Your AI-powered email assistant is ready to help you manage your inbox.
                    </p>

                    {/* Chatbot Interface - Placeholder for now */}
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                        <svg
                            className="w-16 h-16 text-gray-400 mx-auto mb-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                            />
                        </svg>
                        <h3 className="text-lg font-medium text-gray-900 mb-2">
                            Chatbot Interface Coming Soon
                        </h3>
                        <p className="text-gray-600">
                            The AI chatbot will be implemented in Phase 2
                        </p>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
