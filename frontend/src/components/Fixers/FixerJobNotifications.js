import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';

// FixerJobNotifications Component - Job Allocation System v2.1.0  
const FixerJobNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [markingRead, setMarkingRead] = useState({});
  const [applyingJobs, setApplyingJobs] = useState({});
  const { user } = useAuth();

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      
      // Debug logging for production
      console.log('🔍 Fetching notifications - Environment:', {
        NODE_ENV: process.env.NODE_ENV,
        BACKEND_URL: process.env.REACT_APP_BACKEND_URL,
        currentHost: window.location.host,
        apiBaseUrl: process.env.REACT_APP_BACKEND_URL || 'relative'
      });
      
      // Check if user is authenticated
      const token = localStorage.getItem('fixmate_token');
      if (!token) {
        console.warn('No authentication token found');
        setNotifications([]);
        setUnreadCount(0);
        return;
      }

      console.log('🔍 Making API call to notifications endpoint...');
      const response = await apiService.getFixerNotifications();
      console.log('🔍 Notifications API response:', response);
      
      if (response?.data?.success) {
        setNotifications(response.data.notifications || []);
        setUnreadCount(response.data.unread_count || 0);
        console.log('✅ Notifications loaded successfully:', response.data.notifications?.length || 0);
      } else {
        console.warn('Failed to fetch notifications:', response?.data?.message);
        setNotifications([]);
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('❌ Error fetching notifications:', error);
      console.error('❌ Error details:', {
        message: error.message,
        status: error.response?.status,
        statusText: error.response?.statusText,
        url: error.config?.url,
        baseURL: error.config?.baseURL
      });
      
      // Set empty state instead of leaving undefined
      setNotifications([]);
      setUnreadCount(0);
      
      // Don't throw the error - handle gracefully
      if (error.response?.status === 401) {
        console.warn('Authentication failed - user may need to log in again');
      }
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    if (markingRead[notificationId]) return;
    
    try {
      setMarkingRead(prev => ({ ...prev, [notificationId]: true }));
      const response = await apiService.markNotificationRead(notificationId);
      
      if (response.data.success) {
        // Update the notification in the local state
        setNotifications(prev => prev.map(notification => 
          notification.id === notificationId 
            ? { ...notification, is_read: true }
            : notification
        ));
        
        // Update unread count
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    } finally {
      setMarkingRead(prev => ({ ...prev, [notificationId]: false }));
    }
  };

  const applyForJob = async (jobId, notificationId) => {
    if (applyingJobs[jobId]) return;
    
    try {
      setApplyingJobs(prev => ({ ...prev, [jobId]: true }));
      const response = await apiService.applyForJob(jobId);
      
      if (response.data.success) {
        alert('✅ ' + response.data.message);
        
        // Mark the notification as read
        await markAsRead(notificationId);
        
        // Refresh notifications to get updated status
        fetchNotifications();
      } else {
        alert('❌ ' + (response.data.message || 'Failed to apply for job'));
      }
    } catch (error) {
      console.error('Error applying for job:', error);
      if (error.response?.status === 403) {
        alert('❌ Job is no longer available or has been assigned to another fixer');
      } else {
        alert('❌ Failed to apply for job. Please try again.');
      }
    } finally {
      setApplyingJobs(prev => ({ ...prev, [jobId]: false }));
    }
  };

  const getNotificationIcon = (notificationType) => {
    switch (notificationType) {
      case 'job_assigned': return '🎯';
      case 'job_available': return '📋';
      case 'job_cancelled': return '❌';
      case 'job_completed': return '✅';
      default: return '🔔';
    }
  };

  const getNotificationColor = (notificationType, isRead) => {
    if (isRead) return 'bg-gray-50 border-gray-200';
    
    switch (notificationType) {
      case 'job_assigned': return 'bg-green-50 border-green-200';
      case 'job_available': return 'bg-blue-50 border-blue-200';
      case 'job_cancelled': return 'bg-red-50 border-red-200';
      default: return 'bg-orange-50 border-orange-200';
    }
  };

  useEffect(() => {
    // Only fetch if user exists and has proper authentication
    if (user && user.id) {
      try {
        fetchNotifications();
        
        // Set up polling for new notifications every 30 seconds
        const interval = setInterval(() => {
          try {
            fetchNotifications();
          } catch (error) {
            console.error('Error in notification polling:', error);
          }
        }, 30000);
        
        return () => clearInterval(interval);
      } catch (error) {
        console.error('Error setting up notifications:', error);
        // Set safe defaults
        setNotifications([]);
        setUnreadCount(0);
        setLoading(false);
      }
    } else {
      // No user - set empty state
      setNotifications([]);
      setUnreadCount(0);
      setLoading(false);
    }
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
        <span className="ml-3 text-gray-600">Loading notifications...</span>
      </div>
    );
  }

  // Safety check for user authentication
  if (!user) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
        <div className="text-yellow-400 text-4xl mb-4">🔐</div>
        <h3 className="text-lg font-medium text-yellow-900 mb-2">Authentication Required</h3>
        <p className="text-yellow-600">Please log in to view your job notifications.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <h2 className="text-2xl font-bold text-gray-900">Job Notifications</h2>
          {unreadCount > 0 && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
              {unreadCount} new
            </span>
          )}
        </div>
        <button
          onClick={fetchNotifications}
          disabled={loading}
          className="bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors"
        >
          🔄 Refresh
        </button>
      </div>

      {notifications.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <div className="text-gray-400 text-4xl mb-4">📭</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Job Notifications</h3>
          <p className="text-gray-500">You'll see available job notifications here when they become available.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {notifications.map((notification) => (
            <div
              key={notification.id}
              className={`border rounded-lg p-6 ${getNotificationColor(notification.notification_type, notification.is_read)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <span className="text-lg mr-2">
                      {getNotificationIcon(notification.notification_type)}
                    </span>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {notification.title}
                    </h3>
                    {!notification.is_read && (
                      <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        New
                      </span>
                    )}
                  </div>
                  
                  <p className="text-gray-600 mb-4">{notification.message}</p>
                  
                  {/* Job Details */}
                  {notification.job_details && (
                    <div className="bg-white bg-opacity-50 rounded-md p-3 mb-4">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-2 text-sm">
                        <div><strong>Service:</strong> {notification.job_details.service}</div>
                        <div><strong>Location:</strong> {notification.job_details.location}</div>
                        <div><strong>Price:</strong> R{notification.job_details.estimated_price}</div>
                      </div>
                      <div className="mt-2 text-sm">
                        <strong>Status:</strong> <span className="capitalize">{notification.job_details.job_status}</span>
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{new Date(notification.created_at).toLocaleString()}</span>
                    <span className="capitalize">{notification.notification_type.replace('_', ' ')}</span>
                  </div>
                </div>
                
                <div className="ml-4 space-y-2 flex flex-col">
                  {/* Apply for Job Button (for available jobs) */}
                  {notification.job_id && notification.notification_type === 'job_available' && (
                    <button
                      onClick={() => applyForJob(notification.job_id, notification.id)}
                      disabled={applyingJobs[notification.job_id]}
                      className="bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium"
                    >
                      {applyingJobs[notification.job_id] ? '⏳ Applying...' : '✅ Apply for Job'}
                    </button>
                  )}
                  
                  {/* Mark as Read Button */}
                  {!notification.is_read && (
                    <button
                      onClick={() => markAsRead(notification.id)}
                      disabled={markingRead[notification.id]}
                      className="bg-gray-100 hover:bg-gray-200 disabled:opacity-50 text-gray-700 px-4 py-2 rounded-lg transition-colors text-sm"
                    >
                      {markingRead[notification.id] ? '⏳ Marking...' : '📖 Mark as Read'}
                    </button>
                  )}
                  
                  {/* View Job Details Button */}
                  {notification.job_id && (
                    <button
                      onClick={() => {
                        // Open job details in a new tab or navigate to job details page
                        window.open(`/jobs/${notification.job_id}`, '_blank');
                      }}
                      className="bg-blue-100 hover:bg-blue-200 text-blue-700 px-4 py-2 rounded-lg transition-colors text-sm"
                    >
                      👀 View Details
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FixerJobNotifications;