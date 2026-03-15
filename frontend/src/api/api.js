import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

// Create a central axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Intercept requests to automatically attach Authorization header
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
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
            localStorage.removeItem('token');
            localStorage.removeItem('currentUser');
            window.location.href = '/';
        }
        return Promise.reject(error);
    }
);


const handleRequest = async (requestPromise) => {
    try {
        const response = await requestPromise;
        return response.data;
    } catch (error) {
        console.error("API Error:", error.response?.data || error.message);
        throw error.response?.data || error;
    }
};

/**
 * =======================
 * AUTH APIs
 * =======================
 */

// 1. signup
export const signup = async (name, email, password) => {
    return handleRequest(api.post('/auth/signup', { name, email, password }));
};

// 2. login
export const login = async (email, password) => {
    return handleRequest(api.post('/auth/login', { email, password }));
};

// 3. googleAuth
export const googleAuth = async (id_token) => {
    return handleRequest(api.post('/auth/google', { id_token }));
};

/**
 * =======================
 * INTERVIEW APIs
 * =======================
 */

// 4. startInterview
// Initiates a new interview. Backend returns new session details
export const startInterview = async (payload) => {
    return handleRequest(api.post('/interview/start', payload));
};

// 5. getNextQuestion
// Fetches the next available question for the given session.
// Backend returns next question object or "completed" state.
export const getNextQuestion = async (session_id) => {
    return handleRequest(api.get(`/interview/${session_id}/next`));
};

// 6. submitAnswer
// Submits answer. Backend returns either 'next' or 'completed' status without evaluating immediately.
// student_id is derived server-side from the JWT token
export const submitAnswer = async (session_id, interview_question_id, user_answer) => {
    return handleRequest(
        api.post(`/interview/${session_id}/answer`, {
            interview_question_id,
            user_answer,
        })
    );
};

// 7. getSummary
export const getSummary = async (session_id) => {
    return handleRequest(api.get(`/interview/${session_id}/summary`));
};

// 8. getResult — simple score/total/percentage
export const getResult = async (session_id) => {
    return handleRequest(api.get(`/interview/${session_id}/result`));
};

export default api;
