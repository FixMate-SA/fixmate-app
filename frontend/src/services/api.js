import axios from 'axios';

const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('fixmate_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API functions
export const apiService = {
  // Users
  getUsers: () => api.get('/users'),
  getUser: (id) => api.get(`/users/${id}`),
  createUser: (userData) => api.post('/users', userData),
  updateUser: (id, userData) => api.put(`/users/${id}`, userData),

  // Fixers
  getFixers: () => api.get('/fixers'),
  getFixer: (id) => api.get(`/fixers/${id}`),
  createFixer: (fixerData) => api.post('/fixers', fixerData),
  getFixersByService: (service) => api.get(`/fixers/by-service/${service}`),

  // Jobs
  getJobs: (params = {}) => api.get('/jobs', { params }),
  getJob: (id) => api.get(`/jobs/${id}`),
  createJob: (jobData) => api.post('/jobs', jobData),
  updateJob: (id, jobData) => api.put(`/jobs/${id}`, jobData),

  // Reviews
  getReviews: (params = {}) => api.get('/reviews', { params }),
  createReview: (reviewData) => api.post('/reviews', reviewData),

  // Dashboard
  getDashboard: (userId) => api.get(`/dashboard/${userId}`),

  // Auth
  login: (phone) => api.post('/auth/login', { phone }),
};

export default api;