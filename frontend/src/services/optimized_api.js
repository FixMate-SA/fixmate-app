import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from './api';

// Query Keys for cache management
export const QUERY_KEYS = {
  USERS: 'users',
  USER: (id) => ['user', id],
  JOBS: 'jobs',
  JOB: (id) => ['job', id],
  JOB_INSIGHTS: (id) => ['job-insights', id],
  FIXERS: 'fixers',
  FIXER: (id) => ['fixer', id],
  FIXER_REPUTATION: (id) => ['fixer-reputation', id],
  REVIEWS: 'reviews',
  DASHBOARD: (userId) => ['dashboard', userId],
  SMART_MATCHING: 'smart-matching',
  PHASE_3: 'phase-3',
  PWA_STATUS: 'pwa-status',
  NOTIFICATIONS: 'notifications',
  ADMIN_ANALYTICS: 'admin-analytics',
};

// ======= USER QUERIES =======

export const useUser = (userId, options = {}) => {
  return useQuery({
    queryKey: QUERY_KEYS.USER(userId),
    queryFn: () => api.get(`/users/${userId}`).then(res => res.data),
    enabled: !!userId,
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options
  });
};

export const useUpdateUser = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ userId, userData }) => api.put(`/users/${userId}`, userData),
    onSuccess: (data, variables) => {
      // Update the user cache
      queryClient.setQueryData(QUERY_KEYS.USER(variables.userId), data);
      // Invalidate related queries
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.USERS] });
    },
  });
};

// ======= JOB QUERIES =======

export const useJobs = (params = {}, options = {}) => {
  return useQuery({
    queryKey: [QUERY_KEYS.JOBS, params],
    queryFn: () => {
      const searchParams = new URLSearchParams(params);
      return api.get(`/jobs?${searchParams}`).then(res => res.data);
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options
  });
};

export const useJob = (jobId, options = {}) => {
  return useQuery({
    queryKey: QUERY_KEYS.JOB(jobId),
    queryFn: () => api.get(`/jobs/${jobId}`).then(res => res.data),
    enabled: !!jobId,
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options
  });
};

export const useJobInsights = (jobData, options = {}) => {
  return useQuery({
    queryKey: [QUERY_KEYS.JOB_INSIGHTS, jobData],
    queryFn: () => api.post('/smart-matching/job-insights', jobData).then(res => res.data),
    enabled: !!jobData?.service && !!jobData?.location,
    staleTime: 1000 * 60 * 10, // 10 minutes
    ...options
  });
};

export const useCreateJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (jobData) => api.post('/jobs', jobData),
    onSuccess: () => {
      // Invalidate and refetch jobs list
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.JOBS] });
    },
  });
};

export const useUpdateJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ jobId, jobData }) => api.put(`/jobs/${jobId}`, jobData),
    onSuccess: (data, variables) => {
      // Update specific job cache
      queryClient.setQueryData(QUERY_KEYS.JOB(variables.jobId), data);
      // Invalidate jobs list
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.JOBS] });
    },
  });
};

// ======= FIXER QUERIES =======

export const useFixers = (params = {}, options = {}) => {
  return useQuery({
    queryKey: [QUERY_KEYS.FIXERS, params],
    queryFn: () => {
      const searchParams = new URLSearchParams(params);
      return api.get(`/fixers?${searchParams}`).then(res => res.data);
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options
  });
};

export const useFixer = (fixerId, options = {}) => {
  return useQuery({
    queryKey: QUERY_KEYS.FIXER(fixerId),
    queryFn: () => api.get(`/fixers/${fixerId}`).then(res => res.data),
    enabled: !!fixerId,
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options
  });
};

export const useFixerReputation = (fixerId, options = {}) => {
  return useQuery({
    queryKey: QUERY_KEYS.FIXER_REPUTATION(fixerId),
    queryFn: () => api.getFixerReputation(fixerId).then(res => res.data),
    enabled: !!fixerId,
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options
  });
};

export const useInitializeFixerReputation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (fixerId) => api.initializeFixerReputation(fixerId),
    onSuccess: (data, fixerId) => {
      // Update reputation cache
      queryClient.setQueryData(QUERY_KEYS.FIXER_REPUTATION(fixerId), data);
    },
  });
};

// ======= SMART MATCHING QUERIES =======

export const useSmartMatching = (jobData, options = {}) => {
  return useQuery({
    queryKey: [QUERY_KEYS.SMART_MATCHING, jobData],
    queryFn: () => api.post('/smart-matching/find-fixers', jobData).then(res => res.data),
    enabled: !!jobData?.service && !!jobData?.location,
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options
  });
};

export const useMatchFixer = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ fixerId, jobData }) => api.post(`/smart-matching/test-fixer/${fixerId}`, jobData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.SMART_MATCHING] });
    },
  });
};

// ======= DASHBOARD QUERIES =======

export const useDashboard = (userId, options = {}) => {
  return useQuery({
    queryKey: QUERY_KEYS.DASHBOARD(userId),
    queryFn: () => api.getDashboard(userId).then(res => res.data),
    enabled: !!userId,
    staleTime: 1000 * 60 * 2, // 2 minutes
    refetchOnWindowFocus: true,
    ...options
  });
};

// ======= REVIEW QUERIES =======

export const useReviews = (params = {}, options = {}) => {
  return useQuery({
    queryKey: [QUERY_KEYS.REVIEWS, params],
    queryFn: () => {
      const searchParams = new URLSearchParams(params);
      return api.get(`/reviews?${searchParams}`).then(res => res.data);
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options
  });
};

export const useCreateReview = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (reviewData) => api.post('/reviews', reviewData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.REVIEWS] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.FIXERS] });
    },
  });
};

// ======= PHASE 3 QUERIES =======

export const useJobTracking = (jobId, options = {}) => {
  return useQuery({
    queryKey: ['job-tracking', jobId],
    queryFn: () => api.getJobTrackingStatus(jobId).then(res => res.data),
    enabled: !!jobId,
    refetchInterval: 5000, // Refetch every 5 seconds for real-time updates
    staleTime: 0, // Always consider stale for real-time data
    ...options
  });
};

export const useStartJobTracking = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ jobId, departureLocation }) => api.startJobTracking(jobId, departureLocation),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['job-tracking', variables.jobId] });
    },
  });
};

export const useUpdateJobTrackingLocation = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ jobId, location, accuracy }) => api.updateJobTrackingLocation(jobId, location, accuracy),
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['job-tracking', variables.jobId] });
    },
  });
};

export const useCompleteJobTracking = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (jobId) => api.completeJobTracking(jobId),
    onSuccess: (data, jobId) => {
      queryClient.invalidateQueries({ queryKey: ['job-tracking', jobId] });
    },
  });
};

// ======= AI ASSISTANT QUERIES =======

export const useStartAIChat = () => {
  return useMutation({
    mutationFn: ({ language, userType }) => api.startAIChat(language, userType),
  });
};

export const useSendAIChatMessage = () => {
  return useMutation({
    mutationFn: ({ sessionId, message, language }) => api.sendAIChatMessage(sessionId, message, language),
  });
};

export const useEndAIChat = () => {
  return useMutation({
    mutationFn: ({ sessionId, satisfactionRating, resolutionStatus }) => 
      api.endAIChat(sessionId, satisfactionRating, resolutionStatus),
  });
};

// ======= ADMIN QUERIES =======

export const useAdminAnalytics = (type, options = {}) => {
  return useQuery({
    queryKey: [QUERY_KEYS.ADMIN_ANALYTICS, type],
    queryFn: () => {
      switch (type) {
        case 'gamification':
          return api.getGamificationStats().then(res => res.data);
        case 'ai-chat':
          return api.getAIChatAnalytics().then(res => res.data);
        default:
          throw new Error(`Unknown analytics type: ${type}`);
      }
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
    ...options
  });
};

// ======= PUSH NOTIFICATION QUERIES =======

export const usePushSubscriptions = (options = {}) => {
  return useQuery({
    queryKey: [QUERY_KEYS.NOTIFICATIONS, 'subscriptions'],
    queryFn: () => api.get('/push/subscriptions').then(res => res.data),
    staleTime: 1000 * 60 * 10, // 10 minutes
    ...options
  });
};

export const useSubscribeToPush = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (subscriptionData) => api.post('/push/subscribe', subscriptionData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.NOTIFICATIONS, 'subscriptions'] });
    },
  });
};

export const useSendPushNotification = () => {
  return useMutation({
    mutationFn: (notificationData) => api.post('/push/send', notificationData),
  });
};

// ======= PWA QUERIES =======

export const usePWAStatus = (options = {}) => {
  return useQuery({
    queryKey: [QUERY_KEYS.PWA_STATUS],
    queryFn: () => {
      if (window.pwaService) {
        return Promise.resolve(window.pwaService.getPWAStatus());
      }
      return Promise.resolve(null);
    },
    staleTime: 1000 * 30, // 30 seconds
    ...options
  });
};

export const useStartPWASession = () => {
  return useMutation({
    mutationFn: (sessionData) => api.post('/pwa/session/start', sessionData),
  });
};

export const useEndPWASession = () => {
  return useMutation({
    mutationFn: ({ sessionId, sessionData }) => api.post(`/pwa/session/${sessionId}/end`, sessionData),
  });
};

export const useQueueOfflineAction = () => {
  return useMutation({
    mutationFn: (actionData) => api.post('/pwa/offline-action', actionData),
  });
};

export const useOfflineActions = (params = {}, options = {}) => {
  return useQuery({
    queryKey: ['offline-actions', params],
    queryFn: () => {
      const searchParams = new URLSearchParams(params);
      return api.get(`/pwa/offline-actions?${searchParams}`).then(res => res.data);
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options
  });
};

// ======= CUSTOM HOOKS FOR COMPLEX OPERATIONS =======

// Optimistic job creation with offline support
export const useOptimisticJobCreation = () => {
  const queryClient = useQueryClient();
  const createJobMutation = useCreateJob();
  const queueOfflineAction = useQueueOfflineAction();
  
  return useMutation({
    mutationFn: async (jobData) => {
      // Check if online
      if (navigator.onLine) {
        return createJobMutation.mutateAsync(jobData);
      } else {
        // Queue for offline sync
        await queueOfflineAction.mutateAsync({
          action_type: 'create_job',
          action_data: jobData,
          session_id: localStorage.getItem('current_session_id') || 'offline',
          priority: 'high'
        });
        
        // Return optimistic response
        return { 
          success: true, 
          job: { ...jobData, id: `temp-${Date.now()}`, status: 'pending_sync' },
          offline: true 
        };
      }
    },
    onSuccess: (data, variables) => {
      if (!data.offline) {
        // Update cache with real data
        queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.JOBS] });
      } else {
        // Add optimistic update to cache
        queryClient.setQueryData([QUERY_KEYS.JOBS], (oldData) => {
          if (!oldData) return { jobs: [data.job] };
          return { ...oldData, jobs: [data.job, ...oldData.jobs] };
        });
      }
    },
  });
};

// Infinite query for large lists with virtual scrolling support
export const useInfiniteJobs = (params = {}, options = {}) => {
  return useQuery({
    queryKey: [QUERY_KEYS.JOBS, 'infinite', params],
    queryFn: ({ pageParam = 0 }) => {
      const searchParams = new URLSearchParams({
        ...params,
        skip: pageParam,
        limit: 20
      });
      return api.get(`/jobs?${searchParams}`).then(res => res.data);
    },
    getNextPageParam: (lastPage, pages) => {
      if (lastPage.jobs && lastPage.jobs.length === 20) {
        return pages.length * 20;
      }
      return undefined;
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
    ...options
  });
};

// Real-time job status with automatic polling
export const useRealTimeJobStatus = (jobId, options = {}) => {
  return useQuery({
    queryKey: ['job-status-realtime', jobId],
    queryFn: () => api.get(`/jobs/${jobId}`).then(res => res.data),
    enabled: !!jobId,
    refetchInterval: (data) => {
      // Poll faster if job is active, slower if completed
      if (data?.status === 'in_progress' || data?.status === 'assigned') {
        return 5000; // 5 seconds
      } else if (data?.status === 'completed' || data?.status === 'cancelled') {
        return false; // Stop polling
      }
      return 30000; // 30 seconds for other statuses
    },
    refetchIntervalInBackground: true,
    staleTime: 0, // Always consider stale for real-time updates
    ...options
  });
};

export default {
  // Export all hooks for easy importing
  useUser,
  useUpdateUser,
  useJobs,
  useJob,
  useJobInsights,
  useCreateJob,
  useUpdateJob,
  useFixers,
  useFixer,
  useFixerReputation,
  useInitializeFixerReputation,
  useSmartMatching,
  useMatchFixer,
  useDashboard,
  useReviews,
  useCreateReview,
  useJobTracking,
  useStartJobTracking,
  useUpdateJobTrackingLocation,
  useCompleteJobTracking,
  useStartAIChat,
  useSendAIChatMessage,
  useEndAIChat,
  useAdminAnalytics,
  usePushSubscriptions,
  useSubscribeToPush,
  useSendPushNotification,
  usePWAStatus,
  useStartPWASession,
  useEndPWASession,
  useQueueOfflineAction,
  useOfflineActions,
  useOptimisticJobCreation,
  useInfiniteJobs,
  useRealTimeJobStatus,
  QUERY_KEYS
};