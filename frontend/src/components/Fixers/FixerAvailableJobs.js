import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';

// FixerAvailableJobs Component - Job Allocation System v2.1.0
const FixerAvailableJobs = () => {
  const [availableJobs, setAvailableJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [applyingJobs, setApplyingJobs] = useState({});
  const [filter, setFilter] = useState('all');
  const { user } = useAuth();

  const fetchAvailableJobs = async () => {
    try {
      setLoading(true);
      const response = await apiService.getFixerAvailableJobs();
      
      if (response.data.success) {
        setAvailableJobs(response.data.available_jobs || []);
      } else {
        console.error('Failed to fetch available jobs:', response.data.message);
      }
    } catch (error) {
      console.error('Error fetching available jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const applyForJob = async (jobId) => {
    if (applyingJobs[jobId]) return;
    
    try {
      setApplyingJobs(prev => ({ ...prev, [jobId]: true }));
      const response = await apiService.applyForJob(jobId);
      
      if (response.data.success) {
        alert('✅ ' + response.data.message);
        
        // Refresh available jobs to get updated status
        fetchAvailableJobs();
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

  const getPriorityColor = (priorityLevel) => {
    switch (priorityLevel?.toLowerCase()) {
      case 'urgent': return 'border-red-200 bg-red-50';
      case 'high': return 'border-yellow-200 bg-yellow-50';
      case 'medium': return 'border-blue-200 bg-blue-50';
      case 'low': return 'border-green-200 bg-green-50';
      default: return 'border-gray-200 bg-white';
    }
  };

  const getPriorityIcon = (priorityLevel) => {
    switch (priorityLevel?.toLowerCase()) {
      case 'urgent': return '🚨';
      case 'high': return '⚡';
      case 'medium': return '📋';
      case 'low': return '🔧';
      default: return '📝';
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'assigned': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-purple-100 text-purple-800';
      case 'completed': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredJobs = availableJobs.filter(job => {
    if (filter === 'all') return true;
    if (filter === 'urgent') return job.priority_level?.toLowerCase() === 'urgent';
    if (filter === 'high_pay') return job.estimated_price && parseFloat(job.estimated_price) >= 1000;
    if (filter === 'nearby') return true; // Could be enhanced with location filtering
    return true;
  });

  useEffect(() => {
    if (user) {
      fetchAvailableJobs();
      
      // Set up polling for new jobs every 15 seconds
      const interval = setInterval(fetchAvailableJobs, 15000);
      return () => clearInterval(interval);
    }
  }, [user]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
        <span className="ml-3 text-gray-600">Loading available jobs...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
        <div className="flex items-center space-x-3">
          <h2 className="text-2xl font-bold text-gray-900">Available Jobs</h2>
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            {filteredJobs.length} jobs
          </span>
        </div>
        
        {/* Filter Options */}
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium text-gray-700">Filter:</label>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="all">All Jobs</option>
            <option value="urgent">Urgent Only</option>
            <option value="high_pay">High Pay (R1000+)</option>
            <option value="nearby">Nearby</option>
          </select>
          
          <button
            onClick={fetchAvailableJobs}
            disabled={loading}
            className="bg-orange-600 hover:bg-orange-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors text-sm"
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {filteredJobs.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <div className="text-gray-400 text-4xl mb-4">📋</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Available Jobs</h3>
          <p className="text-gray-500">
            {availableJobs.length === 0 
              ? "Check back later for new job opportunities that match your skills."
              : "No jobs match your current filter. Try adjusting the filter options."
            }
          </p>
        </div>
      ) : (
        <div className="grid gap-6">
          {filteredJobs.map((job) => (
            <div 
              key={job.id} 
              className={`border rounded-lg p-6 transition-shadow hover:shadow-lg ${getPriorityColor(job.priority_level)}`}
            >
              <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between space-y-4 lg:space-y-0">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-3">
                    <span className="text-2xl">{getPriorityIcon(job.priority_level)}</span>
                    <div>
                      <h3 className="text-xl font-semibold text-gray-900 capitalize">
                        {job.service?.replace('_', ' ')} Service
                      </h3>
                      <div className="flex items-center space-x-2 mt-1">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                          {job.status?.replace('_', ' ')}
                        </span>
                        {job.priority_level && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                            {job.priority_level} Priority
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <p className="text-gray-700 mb-3">{job.description}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-sm">
                      <div className="flex items-center space-x-2">
                        <span>📍</span>
                        <span className="font-medium">Location:</span>
                        <span>{job.location}</span>
                      </div>
                      
                      {job.estimated_price && (
                        <div className="flex items-center space-x-2">
                          <span>💰</span>
                          <span className="font-medium">Price:</span>
                          <span className="text-green-600 font-semibold">R{job.estimated_price}</span>
                        </div>
                      )}
                      
                      {job.client_name && (
                        <div className="flex items-center space-x-2">
                          <span>👤</span>
                          <span className="font-medium">Client:</span>
                          <span>{job.client_name}</span>
                        </div>
                      )}
                      
                      <div className="flex items-center space-x-2">
                        <span>⏰</span>
                        <span className="font-medium">Posted:</span>
                        <span>{new Date(job.created_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="lg:ml-6 flex flex-col space-y-3">
                  <button
                    onClick={() => applyForJob(job.id)}
                    disabled={applyingJobs[job.id]}
                    className="bg-orange-600 hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-lg transition-colors font-medium"
                  >
                    {applyingJobs[job.id] ? '⏳ Applying...' : '✅ Apply for Job'}
                  </button>
                  
                  <button
                    onClick={() => {
                      // Open job details in a new tab or show more details
                      window.open(`/jobs/${job.id}`, '_blank');
                    }}
                    className="bg-white hover:bg-gray-50 text-gray-700 px-6 py-3 rounded-lg border border-gray-300 transition-colors text-sm"
                  >
                    👀 View Full Details
                  </button>
                  
                  <button
                    onClick={() => {
                      // Show contact information or call client
                      alert(`📞 Contact client: ${job.client_name || 'Client'}\nLocation: ${job.location}`);
                    }}
                    className="bg-blue-50 hover:bg-blue-100 text-blue-700 px-6 py-3 rounded-lg transition-colors text-sm"
                  >
                    📞 Contact Client
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

export default FixerAvailableJobs;