import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';

const Callback = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const { setAuthUser } = useAuth();
    const [error, setError] = useState(null);

    useEffect(() => {
        const handleCallback = async () => {
            const token = searchParams.get('token');
            const errorParam = searchParams.get('error');

            if (errorParam) {
                setError('Authentication failed. Please try again.');
                setTimeout(() => {
                    navigate('/?error=auth_failed');
                }, 2000);
                return;
            }

            if (!token) {
                setError('No authentication token received.');
                setTimeout(() => {
                    navigate('/?error=no_token');
                }, 2000);
                return;
            }

            try {
                localStorage.setItem('access_token', token);
                const userProfile = await authAPI.getCurrentUser();
                setAuthUser(userProfile, token);
                navigate('/dashboard');
            } catch (err) {
                console.error('Callback error:', err);
                setError('Failed to complete authentication.');
                localStorage.removeItem('access_token');
                setTimeout(() => {
                    navigate('/?error=auth_failed');
                }, 2000);
            }
        };

        handleCallback();
    }, [searchParams, navigate, setAuthUser]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="text-center">
                {error ? (
                    <div className="space-y-4">
                        <svg
                            className="w-16 h-16 text-red-500 mx-auto"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                            />
                        </svg>
                        <h2 className="text-xl font-semibold text-gray-900">{error}</h2>
                        <p className="text-gray-600">Redirecting...</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary-600 mx-auto"></div>
                        <h2 className="text-xl font-semibold text-gray-900">
                            Completing sign in...
                        </h2>
                        <p className="text-gray-600">Please wait while we set up your account.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Callback;
