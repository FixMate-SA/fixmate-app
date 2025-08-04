import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import ClientRatingForm from './ClientRatingForm';

const ClientRateJobs = () => {
  const [completedJobs, setCompletedJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJob, setSelectedJob] = useState(null);
  const { user } = useAuth();

  const fetchCompletedJobs = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/jobs/completed`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        // Filter to show only completed jobs that haven't been rated
        const unratedJobs = data.filter(job => 
          job.status === 'completed' && !job.fixer_rating && job.user_id === user.id
        );
        setCompletedJobs(unratedJobs);
      }
    } catch (error) {
      console.error('Error fetching completed jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRatingSubmitted = (result) => {
    // Refresh the jobs list after rating
    fetchCompletedJobs();
    setSelectedJob(null);
  };

  useEffect(() => {
    if (user) {
      fetchCompletedJobs();
    }
  }, [user]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading completed jobs...</span>
        </div>
      </div>
    );
  }

  if (selectedJob) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="mb-6">
          <button
            onClick={() => setSelectedJob(null)}
            className="flex items-center text-blue-600 hover:text-blue-800 mb-4"
          >
            ← Back to Completed Jobs
          </button>
        </div>
        <ClientRatingForm 
          job={selectedJob} 
          onRatingSubmitted={handleRatingSubmitted}
        />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          ⭐ Rate Completed Jobs
        </h1>
        <p className="text-gray-600">
          Help other clients by rating your completed service experiences.
        </p>
      </div>

      {completedJobs.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <div className="text-gray-400 text-4xl mb-4">✅</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Jobs to Rate</h3>
          <p className="text-gray-500 max-w-md mx-auto">
            You don't have any completed jobs that need rating. When fixers complete your jobs, 
            they'll appear here for you to rate and review.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-800">Rate Your Completed Jobs</h3>
                <div className="mt-2 text-sm text-blue-700">
                  <p>Rating fixers helps maintain service quality and helps other clients make informed decisions.</p>
                </div>
              </div>
            </div>
          </div>

          {completedJobs.map((job) => (
            <div key={job.id} className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {job.service?.replace('_', ' ').toUpperCase()}
                    </h3>
                    <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      ✅ Completed
                    </span>
                  </div>
                  
                  <p className="text-gray-600 mb-3">{job.description}</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <p><strong>📍 Location:</strong> {job.location}</p>
                      <p><strong>💰 Price:</strong> R{job.estimated_price || 'TBD'}</p>
                    </div>
                    <div>
                      <p><strong>✅ Completed:</strong> {job.completed_at ? new Date(job.completed_at).toLocaleString() : 'Recently'}</p>
                      <p><strong>📅 Created:</strong> {new Date(job.created_at).toLocaleString()}</p>
                    </div>
                  </div>

                  {/* Before/After Images Preview */}
                  {(job.before_image || job.after_image) && (
                    <div className="mt-4">
                      <p className="text-sm font-medium text-gray-700 mb-2">Work Progress Photos:</p>
                      <div className="grid grid-cols-2 gap-2">
                        {job.before_image && (
                          <div>
                            <p className="text-xs text-gray-500 mb-1">Before:</p>
                            <img
                              src={`data:image/jpeg;base64,${job.before_image}`}
                              alt="Before work"
                              className="w-full h-24 object-cover rounded border"
                            />
                          </div>
                        )}
                        {job.after_image && (
                          <div>
                            <p className="text-xs text-gray-500 mb-1">After:</p>
                            <img
                              src={`data:image/jpeg;base64,${job.after_image}`}
                              alt="After work"
                              className="w-full h-24 object-cover rounded border"
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="ml-4">
                  <button
                    onClick={() => setSelectedJob(job)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition-colors font-medium"
                  >
                    ⭐ Rate Job
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ClientRateJobs;