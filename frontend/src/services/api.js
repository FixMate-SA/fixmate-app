import axios from 'axios';
import { API_BASE_URL } from '../utils/apiConfig';

// Determine the correct API base URL based on environment
const API_BASE = API_BASE_URL;

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

  // AI Services
  transcribeAudio: (audioFile) => {
    const formData = new FormData();
    formData.append('audio', audioFile);
    return api.post('/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  classifyService: (description) => {
    const formData = new FormData();
    formData.append('description', description);
    return api.post('/classify-service', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  analyzeSentiment: (text) => {
    const formData = new FormData();
    formData.append('text', text);
    return api.post('/analyze-sentiment', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // SMS Services
  sendSMS: (toNumber, message) => {
    const formData = new FormData();
    formData.append('to_number', toNumber);
    formData.append('message', message);
    return api.post('/sms/send', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Enhanced Payment Services
  createEFTPayment: (amount, description, userData) => {
    const formData = new FormData();
    formData.append('amount', amount);
    formData.append('description', description);
    formData.append('user_email', userData.email || '');
    formData.append('user_name', userData.name || '');
    return api.post('/payment/eft', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  createCardPayment: (amount, description, userData) => {
    const formData = new FormData();
    formData.append('amount', amount);
    formData.append('description', description);
    formData.append('user_email', userData.email || '');
    formData.append('user_name', userData.name || '');
    return api.post('/payment/eft', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  createAirtimePayment: (phoneNumber, amount, description) => {
    const formData = new FormData();
    formData.append('phone_number', phoneNumber);
    formData.append('amount', amount);
    formData.append('description', description);
    return api.post('/payment/airtime', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  createCashPayment: (location, amount, description) => {
    const formData = new FormData();
    formData.append('location', location);
    formData.append('amount', amount);
    formData.append('description', description);
    return api.post('/payment/cash', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  createStokvelPayment: (stokvelName, amount, description) => {
    const formData = new FormData();
    formData.append('stokvel_name', stokvelName);
    formData.append('amount', amount);
    formData.append('description', description);
    return api.post('/payment/stokvel', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  createLaybyPayment: (totalAmount, depositAmount, description, installments) => {
    const formData = new FormData();
    formData.append('total_amount', totalAmount);
    formData.append('deposit_amount', depositAmount);
    formData.append('description', description);
    formData.append('installments', installments);
    return api.post('/payment/layby', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Phase 3: Real-Time Job Tracking
  startJobTracking: (jobId, departureLocation) => {
    return api.post(`/jobs/${jobId}/tracking/start`, {
      departure_location: departureLocation
    });
  },

  updateJobTrackingLocation: (jobId, location, accuracy) => {
    return api.post(`/jobs/${jobId}/tracking/location`, {
      location,
      accuracy
    });
  },

  completeJobTracking: (jobId) => {
    return api.post(`/jobs/${jobId}/tracking/complete`);
  },

  getJobTrackingStatus: (jobId) => {
    return api.get(`/jobs/${jobId}/tracking/status`);
  },

  // Phase 3: Gamification System
  getFixerReputation: (fixerId) => {
    return api.get(`/fixer/${fixerId}/reputation`);
  },

  initializeFixerReputation: (fixerId) => {
    return api.post(`/fixer/${fixerId}/reputation/initialize`);
  },

  updateFixerPerformance: (fixerId, performanceData) => {
    return api.post(`/fixer/${fixerId}/reputation/update`, performanceData);
  },

  // Phase 3: AI Multilingual Assistant
  startAIChat: (language, userType) => {
    return api.post('/ai-chat/start', {
      language,
      user_type: userType
    });
  },

  sendAIChatMessage: (sessionId, message, language) => {
    return api.post(`/ai-chat/${sessionId}/message`, {
      message,
      language
    });
  },

  endAIChat: (sessionId, satisfactionRating, resolutionStatus) => {
    return api.post(`/ai-chat/${sessionId}/end`, {
      satisfaction_rating: satisfactionRating,
      resolution_status: resolutionStatus
    });
  },

  getAIChatHistory: (sessionId) => {
    return api.get(`/ai-chat/${sessionId}/history`);
  },

  startAnonymousAIChat: (language) => {
    return api.post('/ai-chat/anonymous/start', {
      language
    });
  },

  // Phase 3: Admin Analytics
  getGamificationStats: () => {
    return api.get('/admin/gamification/stats');
  },

  getAIChatAnalytics: () => {
    return api.get('/admin/ai-chat/analytics');
  },

  verifyPayment: (paymentId, paymentType) => {
    const formData = new FormData();
    formData.append('payment_id', paymentId);
    formData.append('payment_type', paymentType);
    return api.post('/payment/verify', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Fixer Payment Management
  getFixerPaymentStatus: (fixerId) => api.get(`/fixer/${fixerId}/payment-status`),
  getFixerPaymentHistory: (fixerId) => api.get(`/fixer/${fixerId}/payment-history`),
  createFixerServiceFee: (fixerId, description) => {
    const formData = new FormData();
    formData.append('description', description);
    return api.post(`/fixer/${fixerId}/create-service-fee`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  settleFixerPayment: (paymentId, paymentMethod, reference) => {
    const formData = new FormData();
    formData.append('payment_method', paymentMethod);
    formData.append('reference', reference);
    return api.post(`/fixer/payment/${paymentId}/settle`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  // WhatsApp Statistics
  getWhatsAppStats: (hours = 24) => api.get('/whatsapp/statistics', { params: { hours } }),

  // Announcements
  getAnnouncements: () => api.get('/announcements'),
  createAnnouncement: (announcementData) => api.post('/admin/announcements', announcementData),
  updateAnnouncement: (id, announcementData) => api.put(`/admin/announcements/${id}`, announcementData),
  deleteAnnouncement: (id) => api.delete(`/admin/announcements/${id}`),
  getAdminAnnouncements: () => api.get('/admin/announcements'),
  
  // Announcement Chat
  getAnnouncementChat: (announcementId, params = {}) => api.get(`/announcements/${announcementId}/chat`, { params }),
  postChatMessage: (announcementId, message) => api.post(`/announcements/${announcementId}/chat`, { message }),
  deleteChatMessage: (announcementId, messageId) => api.delete(`/announcements/${announcementId}/chat/${messageId}`),

  // Fixer Job Allocation System - NEW ENDPOINTS
  getFixerAvailableJobs: () => api.get('/fixer/available-jobs'),
  getFixerNotifications: () => api.get('/fixer/notifications'),
  markNotificationRead: (notificationId) => api.post(`/fixer/notifications/${notificationId}/mark-read`),
  
  // Job Application (from existing apply-for-job endpoint)
  applyForJob: (jobId) => api.post(`/jobs/${jobId}/apply-for-job`),

  // Generic API methods
  get: (endpoint, options = {}) => api.get(endpoint, options),
  post: (endpoint, data, options = {}) => api.post(endpoint, data, options),
  put: (endpoint, data, options = {}) => api.put(endpoint, data, options),
  delete: (endpoint, options = {}) => api.delete(endpoint, options),

  // Offline Support
  syncOfflineData: (offlineData) => api.post('/offline/sync', offlineData),
  getOfflineStatus: () => api.get('/offline/status'),

  // USSD Support
  getUSSDStats: () => api.get('/ussd/stats'),
};

export default api;