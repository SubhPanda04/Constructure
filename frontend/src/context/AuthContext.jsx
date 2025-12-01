import { createContext, useContext, useState, useEffect } from 'react';
import { authAPI } from '../services/api';

const AuthContext = createContext(null);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Check if user is already logged in
    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('access_token');
            const savedUser = localStorage.getItem('user_profile');

            if (token && savedUser) {
                try {
                    // Verify token is still valid by fetching user info
                    const userProfile = await authAPI.getCurrentUser();
                    setUser(userProfile);
                    localStorage.setItem('user_profile', JSON.stringify(userProfile));
                } catch (err) {
                    // Token is invalid, clear storage
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('user_profile');
                    setUser(null);
                }
            }
            setLoading(false);
        };

        initAuth();
    }, []);

    const login = () => {
        authAPI.login();
    };

    const logout = async () => {
        try {
            await authAPI.logout();
            setUser(null);
            window.location.href = '/';
        } catch (err) {
            console.error('Logout error:', err);
            // Force logout even if API call fails
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_profile');
            setUser(null);
            window.location.href = '/';
        }
    };

    const setAuthUser = (userProfile, token) => {
        setUser(userProfile);
        localStorage.setItem('access_token', token);
        localStorage.setItem('user_profile', JSON.stringify(userProfile));
    };

    const value = {
        user,
        loading,
        error,
        login,
        logout,
        setAuthUser,
        isAuthenticated: !!user,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
