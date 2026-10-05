/**
 * API service — Axios instance with JWT interceptor
 * for all backend communication.
 */

import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Request interceptor: attach JWT token ────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('resumexpert_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response interceptor: handle 401 ─────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('resumexpert_token');
      localStorage.removeItem('resumexpert_user');
      // Only redirect if not already on auth pages
      if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// ── Auth APIs ────────────────────────────────────────────
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  verifyOtp: (data) => api.post('/auth/verify-otp', data),
  resendOtp: (data) => api.post('/auth/resend-otp', data),
  login: (data) => api.post('/auth/login', data),
  getProfile: () => api.get('/auth/me'),
};

// ── Resume APIs ──────────────────────────────────────────
export const resumeAPI = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: () => api.get('/resumes/'),
  get: (id) => api.get(`/resumes/${id}`),
  delete: (id) => api.delete(`/resumes/${id}`),
};

// ── Job Description APIs ─────────────────────────────────
export const jobAPI = {
  create: (data) => api.post('/jobs/', data),
  list: () => api.get('/jobs/'),
  get: (id) => api.get(`/jobs/${id}`),
  delete: (id) => api.delete(`/jobs/${id}`),
};

// ── Analysis APIs ────────────────────────────────────────
export const analysisAPI = {
  run: (data) => api.post('/analysis/', data),
  get: (id) => api.get(`/analysis/${id}`),
  history: () => api.get('/analysis/history'),
  dashboard: () => api.get('/analysis/dashboard'),
  suggestions: (id) => api.get(`/analysis/${id}/suggestions`),
};

export default api;
