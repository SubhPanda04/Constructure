import { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const Login = () => {
    const { login, isAuthenticated } = useAuth();

    useEffect(() => {
        if (isAuthenticated) {
            window.location.href = '/dashboard';
        }
    }, [isAuthenticated]);

    // Check for error in URL params
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');
    const errorMessage = urlParams.get('message');

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 via-white to-primary-100">
            <div className="max-w-md w-full mx-4">
                <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
                    {/* Logo/Icon */}
                    <div className="text-center">
                        <div className="mx-auto w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mb-4">
                            <svg
                                className="w-8 h-8 text-white"
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
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">
                            AI Email Assistant
                        </h1>
                        <p className="text-gray-600">
                            Your intelligent email companion powered by AI
                        </p>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                            <div className="flex items-start">
                                <svg
                                    className="w-5 h-5 text-red-600 mt-0.5 mr-3"
                                    fill="currentColor"
                                    viewBox="0 0 20 20"
                                >
                                    <path
                                        fillRule="evenodd"
                                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                                        clipRule="evenodd"
                                    />
                                </svg>
                                <div>
                                    <h3 className="text-sm font-medium text-red-800">
                                        {error === 'session_expired'
                                            ? 'Session Expired'
                                            : 'Authentication Failed'}
                                    </h3>
                                    <p className="text-sm text-red-700 mt-1">
                                        {errorMessage || 'Please try logging in again.'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Features */}
                    <div className="space-y-3">
                        <div className="flex items-start">
                            <svg
                                className="w-5 h-5 text-primary-600 mt-0.5 mr-3"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path
                                    fillRule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clipRule="evenodd"
                                />
                            </svg>
                            <div>
                                <p className="text-sm font-medium text-gray-900">
                                    Read & Summarize Emails
                                </p>
                                <p className="text-xs text-gray-600">
                                    AI-powered email summaries
                                </p>
                            </div>
                        </div>
                        <div className="flex items-start">
                            <svg
                                className="w-5 h-5 text-primary-600 mt-0.5 mr-3"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path
                                    fillRule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clipRule="evenodd"
                                />
                            </svg>
                            <div>
                                <p className="text-sm font-medium text-gray-900">
                                    Generate Smart Replies
                                </p>
                                <p className="text-xs text-gray-600">
                                    Context-aware responses
                                </p>
                            </div>
                        </div>
                        <div className="flex items-start">
                            <svg
                                className="w-5 h-5 text-primary-600 mt-0.5 mr-3"
                                fill="currentColor"
                                viewBox="0 0 20 20"
                            >
                                <path
                                    fillRule="evenodd"
                                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                                    clipRule="evenodd"
                                />
                            </svg>
                            <div>
                                <p className="text-sm font-medium text-gray-900">
                                    Manage Your Inbox
                                </p>
                                <p className="text-xs text-gray-600">
                                    Delete and organize emails
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Login Button */}
                    <button
                        onClick={login}
                        className="w-full bg-white border-2 border-gray-300 rounded-lg px-6 py-3 flex items-center justify-center hover:bg-gray-50 transition-colors duration-200 shadow-sm hover:shadow-md"
                    >
                        <svg className="w-5 h-5 mr-3" viewBox="0 0 24 24">
                            <path
                                fill="#4285F4"
                                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                            />
                            <path
                                fill="#34A853"
                                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                            />
                            <path
                                fill="#FBBC05"
                                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                            />
                            <path
                                fill="#EA4335"
                                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                            />
                        </svg>
                        <span className="text-gray-700 font-medium">
                            Sign in with Google
                        </span>
                    </button>

                    {/* Privacy Notice */}
                    <p className="text-xs text-gray-500 text-center">
                        By signing in, you agree to allow this app to access your Gmail
                        account for reading, sending, and managing emails.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Login;
