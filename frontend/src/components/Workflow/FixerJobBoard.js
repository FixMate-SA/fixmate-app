import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { API_BASE_URL } from '../../utils/apiConfig';

const FixerJobBoard = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  
  const [availableJobs, setAvailableJobs] = useState([]);
  const [currentJob, setCurrentJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(null);
  const [cancelling, setCancelling] = useState(null);
  const [fixerInfo, setFixerInfo] = useState(null);

  useEffect(() => {
    fetchFixerInfo();
  }, [user]);

  useEffect(() => {
    if (fixerInfo?.id) {
      fetchAvailableJobs();
      fetchCurrentJob();
      
      // Set up polling for new jobs and current job status
      const interval = setInterval(() => {
        fetchAvailableJobs();
        fetchCurrentJob();
      }, 5000); // Poll every 5 seconds
      
      return () => clearInterval(interval);
    }
  }, [fixerInfo]);

  const fetchFixerInfo = async () => {
    if (!user?.phone) return;

    try {
      const response = await fetch(`${API_BASE_URL}/fixers`);
      if (response.ok) {
        const data = await response.json();
        
        // Try to find fixer by phone number
        let currentFixer = data.data?.find(f => f.phone === user.phone);
        
        // If not found by phone, try to find by user ID or create a basic fixer profile
        if (!currentFixer && user?.id) {
          currentFixer = data.data?.find(f => f.user_id === user.id);
        }
        
        // If still not found, create a basic fixer info from user data
        if (!currentFixer) {
          currentFixer = {
            id: user.id,
            phone: user.phone,
            name: user.name || 'Fixer',
            rating: user.rating || 5.0,
            availability: 'available',
            user_id: user.id
          };
        }
        
        setFixerInfo(currentFixer);
      } else {
        // If API call fails, create basic fixer info from user data
        setFixerInfo({
          id: user.id,
          phone: user.phone,
          name: user.name || 'Fixer',
          rating: user.rating || 5.0,
          availability: 'available',
          user_id: user.id
        });
      }
    } catch (error) {
      console.error('Error fetching fixer info:', error);
      // Fallback: create basic fixer info from user data
      setFixerInfo({
        id: user.id,
        phone: user.phone,
        name: user.name || 'Fixer',
        rating: user.rating || 5.0,
        availability: 'available',
        user_id: user.id
      });
    }
  };

  const fetchAvailableJobs = async () => {
    if (!fixerInfo?.id) return;

    try {
      const response = await fetch(`${API_BASE_URL}/fixer/${fixerInfo.id}/eligible-jobs`);
      if (response.ok) {
        const data = await response.json();
        setAvailableJobs(data.available_jobs || []);
      }
    } catch (error) {
      console.error('Error fetching available jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentJob = async () => {
    if (!fixerInfo?.id) return;

    try {
      const response = await fetch(`${API_BASE_URL}/jobs`);
      if (response.ok) {
        const data = await response.json();
        // Find the current job assigned to this fixer
        const assignedJob = data.data?.find(job => 
          job.fixer_id === fixerInfo.id && 
          ['assigned', 'in_progress'].includes(job.status)
        );
        setCurrentJob(assignedJob || null);
      }
    } catch (error) {
      console.error('Error fetching current job:', error);
    }
  };

  const cancelJob = async (jobId) => {
    if (!fixerInfo?.id || cancelling || !jobId) return;

    const confirmCancel = window.confirm(
      'Are you sure you want to cancel this job? This will:\n' +
      '• Apply a 2-hour availability freeze\n' +
      '• Apply a 0.2 rating penalty\n' +
      '• Reassign the job to another fixer'
    );

    if (!confirmCancel) return;

    setCancelling(jobId);
    try {
      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fixer_id: fixerInfo.id,
          cancelled_by: 'fixer',
          reason: prompt('Please provide a reason for cancellation:') || 'No reason provided'
        })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        alert('Job cancelled. Penalties applied: 2-hour freeze and 0.2 rating penalty.');
        setCurrentJob(null);
        fetchAvailableJobs(); // Refresh available jobs
      } else {
        alert(result.detail || result.message || 'Failed to cancel job.');
      }
    } catch (error) {
      console.error('Error cancelling job:', error);
      alert('An error occurred while cancelling the job. Please try again.');
    } finally {
      setCancelling(null);
    }
  };

  const acceptJob = async (jobId) => {
    if (!fixerInfo?.id || accepting) return;

    setAccepting(jobId);
    try {
      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/accept`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fixer_id: fixerInfo.id
        })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        alert(t('jobAcceptedSuccess', 'Job accepted successfully! You can now start working on this job.'));
        fetchAvailableJobs(); // Refresh the list
        fetchCurrentJob(); // Refresh current job
      } else {
        alert(result.detail || result.message || t('jobAcceptError', 'Failed to accept job. It may have been taken by another fixer.'));
      }
    } catch (error) {
      console.error('Error accepting job:', error);
      alert(t('jobAcceptErrorGeneric', 'An error occurred while accepting the job. Please try again.'));
    } finally {
      setAccepting(null);
    }
  };

  const formatTimeRemaining = (timeoutString) => {
    if (!timeoutString) return null;
    
    try {
      const timeout = new Date(timeoutString);
      const now = new Date();
      const diff = timeout.getTime() - now.getTime();
      
      if (diff <= 0) return t('expired', 'Expired');
      
      const minutes = Math.floor(diff / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);
      
      return `${minutes}m ${seconds}s`;
    } catch {
      return null;
    }
  };

  const getPriorityColor = (priorityLevel, isEmergency) => {
    if (isEmergency) return 'border-red-500 bg-red-50';
    if (priorityLevel === 'urgent') return 'border-yellow-500 bg-yellow-50';
    return 'border-gray-200 bg-white';
  };

  const getPriorityIcon = (priorityLevel, isEmergency) => {
    if (isEmergency) return '🚨';
    if (priorityLevel === 'urgent') return '⚡';
    return '🔧';
  };

  if (!fixerInfo) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <div className="text-yellow-600 mr-3">⚠️</div>
            <div>
              <h3 className="text-sm font-medium text-yellow-800">
                {t('fixerNotFound', 'Fixer Profile Not Found')}
              </h3>
              <p className="text-sm text-yellow-700 mt-1">
                {t('fixerNotFoundMessage', 'You need to complete your fixer registration to access the job board.')}
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">{t('loadingJobs', 'Loading available jobs...')}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-xl md:text-2xl font-bold text-gray-900 mb-2">
          🎯 {t('availableJobs', 'Available Jobs for Fixers')}
        </h1>
        <p className="text-sm md:text-base text-gray-600">
          {t('availableJobsDescription', 'First come, first serve! Accept jobs that match your skills and location.')}
        </p>
      </div>

      {/* Fixer Status */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${currentJob ? 'bg-orange-500' : 'bg-green-500'}`}></div>
            <span className="text-sm font-medium text-gray-900">
              {t('fixerStatus', 'Status')}: {currentJob ? 'Busy with Job' : t('available', 'Available')}
            </span>
          </div>
          <div className="text-sm text-gray-500">
            {t('autoRefreshNote', 'Auto-refreshing every 5 seconds')}
          </div>
        </div>
      </div>

      {/* Current Job Section */}
      {currentJob && (
        <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-blue-900 mb-2">
                🔧 Current Job: {currentJob.service?.replace('_', ' ').toUpperCase()}
              </h3>
              <div className="space-y-2 text-sm">
                <p><strong>Location:</strong> {currentJob.location}</p>
                <p><strong>Description:</strong> {currentJob.description}</p>
                <p><strong>Price:</strong> R{currentJob.estimated_price || 'TBD'}</p>
                <p><strong>Status:</strong> {currentJob.status}</p>
              </div>
            </div>
            <div className="flex flex-col space-y-2">
              <button
                onClick={() => cancelJob(currentJob.id)}
                disabled={cancelling === currentJob.id}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  cancelling === currentJob.id
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-red-600 text-white hover:bg-red-700'
                }`}
              >
                {cancelling === currentJob.id ? 'Cancelling...' : 'Cancel Job'}
              </button>
              <p className="text-xs text-gray-600 text-center">
                ⚠️ Penalties apply
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Jobs List */}
      {availableJobs.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {currentJob ? 'No New Jobs Available' : t('noJobsAvailable', 'No Jobs Available')}
          </h3>
          <p className="text-gray-600">
            {currentJob 
              ? 'Complete your current job to see new opportunities.'
              : t('noJobsMessage', 'There are currently no jobs available that match your profile. New jobs will appear here automatically.')
            }
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {availableJobs.map((job) => (
            <div
              key={job.job_id}
              className={`rounded-lg border-2 p-6 transition-all ${getPriorityColor(job.priority_level, job.is_emergency)}`}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">
                    {getPriorityIcon(job.priority_level, job.is_emergency)}
                  </span>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      {job.service?.replace('_', ' ').toUpperCase()}
                    </h3>
                    {job.is_emergency && (
                      <span className="inline-block bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                        🚨 {t('emergency', 'EMERGENCY')}
                      </span>
                    )}
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-green-600">
                    R{job.estimated_price || 'TBD'}
                  </div>
                  <div className="text-xs text-gray-500">
                    {formatTimeRemaining(job.assignment_timeout) && (
                      <>⏰ {formatTimeRemaining(job.assignment_timeout)}</>
                    )}
                  </div>
                </div>
              </div>

              <div className="space-y-3 mb-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">
                    📍 {t('location', 'Location')}
                  </h4>
                  <p className="text-sm text-gray-600">{job.location}</p>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-1">
                    📝 {t('description', 'Description')}
                  </h4>
                  <p className="text-sm text-gray-600">{job.description}</p>
                </div>

                {job.scheduled_at && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-1">
                      🕐 {t('scheduledTime', 'Scheduled Time')}
                    </h4>
                    <p className="text-sm text-gray-600">
                      {new Date(job.scheduled_at).toLocaleString()}
                    </p>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between border-t pt-4">
                <div className="text-xs text-gray-500">
                  <span className="mr-4">
                    👤 Client: {job.client_contact || t('anonymous', 'Anonymous')}
                  </span>
                  {job.distance && (
                    <span className="mr-4">
                      📍 Distance: {job.distance}km
                    </span>
                  )}
                  <span>
                    🎯 Match: {job.match_score}%
                  </span>
                </div>

                <button
                  onClick={() => acceptJob(job.job_id)}
                  disabled={accepting === job.job_id || currentJob}
                  className={`px-6 py-2 rounded-md font-medium transition-colors ${
                    accepting === job.job_id || currentJob
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : job.is_emergency
                      ? 'bg-red-600 text-white hover:bg-red-700'
                      : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
                >
                  {accepting === job.job_id 
                    ? t('accepting', 'Accepting...') 
                    : currentJob 
                    ? 'Complete Current Job'
                    : t('acceptJob', 'Accept Job')
                  }
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FixerJobBoard;