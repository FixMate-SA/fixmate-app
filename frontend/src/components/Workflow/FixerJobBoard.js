import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { API_BASE_URL } from '../../utils/apiConfig';
import FixerJobNotifications from '../Fixers/FixerJobNotifications';
import FixerAvailableJobs from '../Fixers/FixerAvailableJobs';
import JobCompletionForm from '../Jobs/JobCompletionForm';
import ErrorBoundary from '../Common/ErrorBoundary';

const FixerJobBoard = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  
  const [availableJobs, setAvailableJobs] = useState([]);
  const [currentJob, setCurrentJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(null);
  const [cancelling, setCancelling] = useState(null);
  const [fixerInfo, setFixerInfo] = useState(null);
  const [activeTab, setActiveTab] = useState('notifications');

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

  const fetchJobsData = () => {
    fetchAvailableJobs();
    fetchCurrentJob();
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
    <div className="max-w-6xl mx-auto p-2 md:p-6">
      <div className="mb-4 md:mb-6">
        <h1 className="text-lg md:text-2xl font-bold text-gray-900 mb-2">
          🎯 {t('fixerJobManagement', 'Fixer Job Management')}
        </h1>
        <p className="text-sm md:text-base text-gray-600">
          {t('fixerJobManagementDesc', 'Manage job notifications, active assignments, and complete work.')}
        </p>
      </div>

      {/* Tab Navigation - Mobile Responsive */}
      <div className="bg-white rounded-lg shadow-sm mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-1 md:space-x-4 px-2 md:px-6 overflow-x-auto scrollbar-hide">
            {[
              { id: 'notifications', label: t('notifications'), icon: '🔔', shortLabel: t('notify', 'Notify') },
              { id: 'active', label: t('activeJobs'), icon: '🔧', shortLabel: t('active', 'Active') },
              { id: 'available', label: t('availableJobs'), icon: '📋', shortLabel: t('jobs', 'Jobs') },
              { id: 'completed', label: t('completed'), icon: '✅', shortLabel: t('done', 'Done') }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-3 md:py-4 px-2 md:px-4 border-b-2 font-medium text-xs md:text-sm flex items-center space-x-1 md:space-x-2 whitespace-nowrap min-w-0 flex-shrink-0 ${
                  activeTab === tab.id
                    ? 'border-orange-500 text-orange-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="text-sm md:text-base">{tab.icon}</span>
                <span className="hidden sm:inline">{tab.label}</span>
                <span className="sm:hidden text-xs">{tab.shortLabel}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-3 md:p-6">
          {activeTab === 'notifications' && (
            <ErrorBoundary 
              title="Error Loading Notifications" 
              message="There was an issue loading your job notifications. Please try refreshing the page or contact support if the problem persists."
            >
              <FixerJobNotifications />
            </ErrorBoundary>
          )}

          {activeTab === 'active' && (
            <div>
              <h3 className="text-base md:text-lg font-semibold text-gray-900 mb-4">{t('activeJobs')}</h3>
              {currentJob ? (
                <div className="space-y-4">
                  <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-3 md:p-6">
                    <div className="flex flex-col md:flex-row md:items-start md:justify-between mb-4">
                      <div className="flex-1">
                        <h4 className="text-base md:text-lg font-semibold text-blue-900 mb-2">
                          🔧 Current Job: {currentJob.service?.replace('_', ' ').toUpperCase()}
                        </h4>
                        <div className="space-y-2 text-sm md:text-base">
                          <p><strong>Location:</strong> {currentJob.location}</p>
                          <p><strong>Description:</strong> {currentJob.description}</p>
                          <p><strong>Status:</strong> {currentJob.status}</p>
                          {currentJob.estimated_price && (
                            <p><strong>Estimated Price:</strong> R{currentJob.estimated_price}</p>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-4">
                      <JobCompletionForm 
                        job={currentJob} 
                        onComplete={() => {
                          fetchJobsData();
                          setActiveTab('completed');
                        }} 
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-4">📭</div>
                  <p className="text-sm md:text-base">{t('noActiveJobs', 'No active jobs at the moment.')}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'available' && (
            <ErrorBoundary 
              title="Error Loading Available Jobs" 
              message="There was an issue loading available jobs. Please try refreshing the page or contact support if the problem persists."
            >
              <FixerAvailableJobs />
            </ErrorBoundary>
          )}

          {activeTab === 'completed' && (
            <div>
              <h3 className="text-base md:text-lg font-semibold text-gray-900 mb-4">{t('completedJobs')}</h3>
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-4">✅</div>
                <p className="text-sm md:text-base">{t('completedJobsWillAppear', 'Your completed jobs will appear here.')}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FixerJobBoard;