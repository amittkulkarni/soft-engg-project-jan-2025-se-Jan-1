import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
    baseURL: process.env.VUE_APP_API_URL || 'https://seek-backend-0qms.onrender.com',
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
});

// Request interceptor for adding auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

//// Response interceptor for handling common errors
//api.interceptors.response.use(
//    (response) => response,
//    (error) => {
//        if (error.response && error.response.status === 401) {
//            // If 401 response returned from api
//            localStorage.removeItem('access_token');
//            // Redirect to login page if needed
//            window.location.href = '/login';
//        }
//        return Promise.reject(error);
//    }
//);

export default api;