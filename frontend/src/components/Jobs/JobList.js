import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/api';
import { Link } from 'react-router-dom';

const JobList = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const response = await apiService.getJobs();
      setJobs(response.data || []);
    } catch (err) {
      console.error('Error fetching jobs:', err);
      setError(t('errorFetchingJobs', 'Failed to fetch jobs. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'assigned':
        return 'bg-blue-100 text-blue-800';
      case 'in_progress':
        return 'bg-orange-100 text-orange-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending':
        return t('pending');
      case 'assigned':
        return t('assigned');
      case 'in_progress':
        return t('inProgress');
      case 'completed':
        return t('completed');
      case 'cancelled':
        return t('cancelled');
      default:
        return status;
    }
  };

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'low':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'high':
        return 'text-orange-600';
      case 'urgent':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getUrgencyText = (urgency) => {
    switch (urgency) {
      case 'low':
        return t('low');
      case 'medium':
        return t('medium');
      case 'high':
        return t('high');
      case 'urgent':
        return t('urgent');
      default:
        return urgency;
    }
  };

  const filteredJobs = jobs.filter(job => {
    const matchesFilter = filter === 'all' || job.status === filter;
    const matchesSearch = job.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         job.description?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
        <p className="ml-4 text-lg text-gray-600">{t('loading')}</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          {t('myJobs')}
        </h1>
        
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          {/* Search */}
          <div className="flex-1">
            <input
              type="text"
              placeholder={t('searchJobs', 'Search jobs...')}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          
          {/* Filter */}
          <div>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">{t('allJobs', 'All Jobs')}</option>
              <option value="pending">{t('pending')}</option>
              <option value="assigned">{t('assigned')}</option>
              <option value="in_progress">{t('inProgress')}</option>
              <option value="completed">{t('completed')}</option>
              <option value="cancelled">{t('cancelled')}</option>
            </select>
          </div>
          
          {/* Create Job Button */}
          <Link
            to="/jobs/create"
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 whitespace-nowrap"
          >
            {t('createNewJob')}
          </Link>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
          <div className="text-sm text-red-600">{error}</div>
        </div>
      )}

      {filteredJobs.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-500 text-lg mb-4">
            {searchTerm || filter !== 'all' 
              ? t('noJobsMatch', 'No jobs match your criteria')
              : t('noJobsYet', 'You haven\'t created any jobs yet')
            }
          </div>
          {(!searchTerm && filter === 'all') && (
            <Link
              to="/jobs/create"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              {t('createFirstJob', 'Create Your First Job')}
            </Link>
          )}
        </div>
      ) : (
        <div className="grid gap-6">
          {filteredJobs.map((job) => (
            <div key={job.id} className="bg-white rounded-lg shadow-md border hover:shadow-lg transition-shadow">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      {job.title}
                    </h3>
                    <p className="text-gray-600 mb-3 line-clamp-2">
                      {job.description}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(job.status)}`}>
                      {getStatusText(job.status)}
                    </span>
                    <span className={`px-2 py-1 text-xs font-medium ${getUrgencyColor(job.urgency)}`}>
                      {getUrgencyText(job.urgency)}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-4">
                  {job.location && (
                    <div>
                      <span className="font-medium">{t('location')}:</span>
                      <span className="ml-1">{job.location}</span>
                    </div>
                  )}
                  
                  {job.category && (
                    <div>
                      <span className="font-medium">{t('category')}:</span>
                      <span className="ml-1">{job.category}</span>
                    </div>
                  )}

                  {(job.budget_min || job.budget_max) && (
                    <div>
                      <span className="font-medium">{t('budget')}:</span>
                      <span className="ml-1">
                        R{job.budget_min || 0} - R{job.budget_max || 0}
                      </span>
                    </div>
                  )}

                  {job.created_at && (
                    <div>
                      <span className="font-medium">{t('created')}:</span>
                      <span className="ml-1">
                        {new Date(job.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  )}
                </div>

                {job.images && job.images.length > 0 && (
                  <div className="mb-4">
                    <div className="flex space-x-2 overflow-x-auto">
                      {job.images.slice(0, 3).map((image, index) => (
                        <img
                          key={index}
                          src={image}
                          alt={`${t('jobImage')} ${index + 1}`}
                          className="w-20 h-20 object-cover rounded-md flex-shrink-0"
                        />
                      ))}
                      {job.images.length > 3 && (
                        <div className="w-20 h-20 bg-gray-200 rounded-md flex items-center justify-center flex-shrink-0">
                          <span className="text-sm text-gray-600">
                            +{job.images.length - 3}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    {t('jobId')}: #{job.id}
                  </div>
                  
                  <div className="flex space-x-2">
                    <button className="px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-blue-500">
                      {t('viewDetails')}
                    </button>
                    
                    {job.status === 'pending' && (
                      <button className="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-50 rounded-md hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-500">
                        {t('edit')}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default JobList;