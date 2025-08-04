import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';

const FixerJobNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  const fetchNotifications = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/fixer/notifications`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const acceptJob = async (jobId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}/accept-fixer`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`
        }
      });
      
      if (response.ok) {
        alert('✅ Job accepted successfully!');
        fetchNotifications(); // Refresh notifications
      } else {
        const error = await response.json();
        alert(`❌ Failed to accept job: ${error.detail}`);
      }
    } catch (error) {
      console.error('Error accepting job:', error);
      alert('❌ Failed to accept job. Please try again.');
    }
  };

  useEffect(() => {
    if (user) {
      fetchNotifications();
    }
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Job Notifications</h2>
        <button
          onClick={fetchNotifications}
          className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg transition-colors"
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
              className={`border rounded-lg p-6 ${
                notification.read 
                  ? 'bg-gray-50 border-gray-200' 
                  : 'bg-orange-50 border-orange-200'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {notification.title}
                    </h3>
                    {!notification.read && (
                      <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        New
                      </span>
                    )}
                  </div>
                  
                  <p className="text-gray-600 mb-4">{notification.message}</p>
                  
                  <div className="text-sm text-gray-500">
                    {new Date(notification.created_at).toLocaleString()}
                  </div>
                </div>
                
                {notification.job_id && (
                  <div className="ml-4 space-y-2">
                    <button
                      onClick={() => acceptJob(notification.job_id)}
                      className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium"
                    >
                      ✅ Accept Job
                    </button>
                    
                    <button
                      className="block w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors text-sm"
                    >
                      👀 View Details
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FixerJobNotifications;