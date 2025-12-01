import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_profile');
            window.location.href = '/?error=session_expired';
        }
        return Promise.reject(error);
    }
);

export const authAPI = {
    login: () => {
        window.location.href = `${API_BASE_URL}/auth/google/login`;
    },

    getCurrentUser: async () => {
        const response = await api.get('/auth/me');
        return response.data;
    },

    logout: async () => {
        await api.post('/auth/logout');
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_profile');
    },
};

export const emailAPI = {
    getRecentEmails: async () => {
        const response = await api.get('/api/emails/recent');
        return response.data;
    },

    generateReply: async (emailId) => {
        const response = await api.post('/api/emails/generate-reply', { email_id: emailId });
        return response.data;
    },

    sendReply: async (emailId, replyContent) => {
        const response = await api.post('/api/emails/send-reply', {
            email_id: emailId,
            content: replyContent,
        });
        return response.data;
    },

    deleteEmail: async (emailId) => {
        const response = await api.delete(`/api/emails/delete/${emailId}`);
        return response.data;
    },
};

export const chatAPI = {
    sendMessage: async (message) => {
        const response = await api.post('/api/chat/message', { message });
        return response.data;
    },
};

export default api;
