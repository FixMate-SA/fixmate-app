import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';

const FixerJobBoard = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  
  const [availableJobs, setAvailableJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(null);
  const [fixerInfo, setFixerInfo] = useState(null);

  useEffect(() => {
    fetchFixerInfo();
    fetchAvailableJobs();
    
    // Set up polling for new jobs
    const interval = setInterval(fetchAvailableJobs, 5000); // Poll every 5 seconds
    
    return () => clearInterval(interval);
  }, [user]);

  const fetchFixerInfo = async () => {
    if (!user?.phone) return;

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/fixers`);
      if (response.ok) {
        const data = await response.json();
        const currentFixer = data.data?.find(f => f.phone === user.phone);
        setFixerInfo(currentFixer);
      }
    } catch (error) {
      console.error('Error fetching fixer info:', error);
    }
  };

  const fetchAvailableJobs = async () => {
    if (!fixerInfo?.id) return;

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/fixer/${fixerInfo.id}/eligible-jobs`);
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

  const acceptJob = async (jobId) => {
    if (!fixerInfo?.id || accepting) return;

    setAccepting(jobId);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}/accept`, {
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
          <div className="flex">
            <div className="flex-shrink-0">
              ⚠️
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                {t('fixerProfileRequired', 'Fixer Profile Required')}
              </h3>
              <p className="mt-1 text-sm text-yellow-700">
                {t('fixerProfileRequiredMessage', 'You need to have an approved fixer profile to view available jobs.')}
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
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          🎯 {t('availableJobs', 'Available Jobs')}
        </h1>
        <p className="text-gray-600">
          {t('availableJobsDescription', 'First come, first serve! Accept jobs that match your skills and location.')}
        </p>
      </div>

      {/* Fixer Status */}
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm font-medium text-gray-900">
              {t('fixerStatus', 'Status')}: {t('available', 'Available')}
            </span>
          </div>
          <div className="text-sm text-gray-500">
            {t('autoRefreshNote', 'Auto-refreshing every 5 seconds')}
          </div>
        </div>
      </div>

      {/* Jobs List */}
      {availableJobs.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <div className="text-4xl mb-4">🔍</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {t('noJobsAvailable', 'No Jobs Available')}
          </h3>
          <p className="text-gray-600">
            {t('noJobsMessage', 'There are currently no jobs available that match your profile. New jobs will appear here automatically.')}
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
                  <p className="text-sm text-gray-600">
                    {job.description.length > 150 
                      ? `${job.description.substring(0, 150)}...` 
                      : job.description
                    }
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <span>
                    🕐 {t('posted', 'Posted')}: {new Date().toLocaleTimeString()}
                  </span>
                  <span>
                    {job.priority_level === 'emergency' 
                      ? t('emergencyPriority', 'Emergency Priority')
                      : t('normalPriority', 'Normal Priority')
                    }
                  </span>
                </div>

                <button
                  onClick={() => acceptJob(job.job_id)}
                  disabled={accepting === job.job_id}
                  className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                    accepting === job.job_id
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : job.is_emergency
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  {accepting === job.job_id ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      {t('accepting', 'Accepting...')}
                    </div>
                  ) : (
                    <>
                      ✋ {t('acceptJob', 'Accept Job')}
                    </>
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Quick Tips */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800 mb-2">
          💡 {t('quickTips', 'Quick Tips')}
        </h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• {t('tip1', 'Jobs are assigned first come, first serve')}</li>
          <li>• {t('tip2', 'You can only have one active job at a time')}</li>
          <li>• {t('tip3', 'Emergency jobs have higher priority and better compensation')}</li>
          <li>• {t('tip4', 'Complete jobs on time to maintain your reliability score')}</li>
          <li>• {t('tip5', 'R20 platform fee applies to each completed job')}</li>
        </ul>
      </div>
    </div>
  );
};

export default FixerJobBoard;