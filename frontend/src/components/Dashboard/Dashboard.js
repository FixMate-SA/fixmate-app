import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import { Link, useNavigate } from 'react-router-dom';
import Logo from '../Common/Logo';

const Dashboard = () => {
  const { user, getUserRole } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const userRole = getUserRole();

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        console.log('Dashboard: Fetching data for user:', user);
        const response = await apiService.getDashboard(user.id);
        console.log('Dashboard: API response:', response);
        setDashboardData(response.data);
      } catch (err) {
        console.error('Dashboard: Error fetching dashboard:', err);
        console.error('Dashboard: Error details:', {
          message: err.message,
          response: err.response?.data,
          status: err.response?.status
        });
        setError(`Failed to load dashboard data: ${err.response?.data?.detail || err.message}`);
      } finally {
        setLoading(false);
      }
    };

    if (user?.id) {
      console.log('Dashboard: User found, fetching data...');
      fetchDashboardData();
    } else {
      console.log('Dashboard: No user ID found:', user);
      setLoading(false);
      setError('User not found');
    }
  }, [user]);

  const getRoleBasedContent = () => {
    switch (userRole) {
      case 'client':
        return {
          title: 'Client Dashboard',
          subtitle: 'Manage your service requests and connect with trusted fixers',
          quickActions: [
            { 
              title: 'Create New Job', 
              desc: 'Post a new service request', 
              path: '/jobs/create', 
              icon: '➕',
              color: 'bg-blue-600 hover:bg-blue-700'
            },
            { 
              title: 'Find Fixers', 
              desc: 'Browse available service providers', 
              path: '/fixers', 
              icon: '🔧',
              color: 'bg-green-600 hover:bg-green-700'
            },
            { 
              title: 'My Jobs', 
              desc: 'View your job requests', 
              path: '/jobs/list', 
              icon: '📋',
              color: 'bg-purple-600 hover:bg-purple-700'
            }
          ],
          stats: [
            { label: 'Active Jobs', value: dashboardData?.stats?.active_jobs || 0, icon: '🔄' },
            { label: 'Completed', value: dashboardData?.stats?.completed_jobs || 0, icon: '✅' },
            { label: 'Total Spent', value: `R${dashboardData?.stats?.total_spent || 0}`, icon: '💰' }
          ]
        };
      case 'fixer':
        return {
          title: 'Fixer Dashboard',
          subtitle: 'Manage your jobs and grow your service business',
          quickActions: [
            { 
              title: 'Available Jobs', 
              desc: 'Browse and accept new jobs', 
              path: '/fixer/jobs', 
              icon: '🔨',
              color: 'bg-green-600 hover:bg-green-700'
            },
            { 
              title: 'My Payments', 
              desc: 'Track earnings and payments', 
              path: '/fixer/payment', 
              icon: '💳',
              color: 'bg-blue-600 hover:bg-blue-700'
            },
            { 
              title: 'Learning Center', 
              desc: 'Improve your skills', 
              path: '/fixer/learning', 
              icon: '🎓',
              color: 'bg-purple-600 hover:bg-purple-700'
            }
          ],
          stats: [
            { label: 'Jobs Completed', value: dashboardData?.stats?.jobs_completed || 0, icon: '✅' },
            { label: 'Rating', value: dashboardData?.stats?.rating || '5.0', icon: '⭐' },
            { label: 'Total Earned', value: `R${dashboardData?.stats?.total_earned || 0}`, icon: '💰' }
          ]
        };
      case 'admin':
        return {
          title: 'Admin Dashboard',
          subtitle: 'Manage the FixMate-SA platform and monitor operations',
          quickActions: [
            { 
              title: 'Admin Panel', 
              desc: 'Platform management tools', 
              path: '/admin/panel', 
              icon: '⚙️',
              color: 'bg-red-600 hover:bg-red-700'
            },
            { 
              title: 'Smart Matching', 
              desc: 'View matching analytics', 
              path: '/admin/smart-matching', 
              icon: '🎯',
              color: 'bg-indigo-600 hover:bg-indigo-700'
            },
            { 
              title: 'Business Tools', 
              desc: 'Business compliance features', 
              path: '/admin/business', 
              icon: '🏢',
              color: 'bg-gray-600 hover:bg-gray-700'
            }
          ],
          stats: [
            { label: 'Total Users', value: dashboardData?.stats?.total_users || 0, icon: '👥' },
            { label: 'Active Jobs', value: dashboardData?.stats?.total_jobs || 0, icon: '🔄' },
            { label: 'Platform Revenue', value: `R${dashboardData?.stats?.platform_revenue || 0}`, icon: '💰' }
          ]
        };
      default:
        return {
          title: 'Dashboard',
          subtitle: 'Welcome to FixMate-SA',
          quickActions: [],
          stats: []
        };
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
        {error}
      </div>
    );
  }

  const { recent_jobs = [], top_fixers = [], stats = {} } = dashboardData || {};

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'assigned':
        return 'bg-yellow-100 text-yellow-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg p-6">
        <h1 className="text-2xl font-bold mb-2">Welcome back, {user.name}!</h1>
        <p className="text-blue-100">Find reliable fixers for all your home repair needs</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-full">
              <span className="text-2xl">📋</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Jobs</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total_jobs || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-full">
              <span className="text-2xl">✅</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-gray-900">{stats.completed_jobs || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-full">
              <span className="text-2xl">⭐</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Success Rate</p>
              <p className="text-2xl font-bold text-gray-900">
                {stats.total_jobs > 0 ? Math.round((stats.completed_jobs / stats.total_jobs) * 100) : 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-4">
          <Link
            to="/jobs/create"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <span className="mr-2">➕</span>
            Create New Job
          </Link>
          <Link
            to="/fixers"
            className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          >
            <span className="mr-2">🔧</span>
            Browse Fixers
          </Link>
          <Link
            to="/jobs"
            className="inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            <span className="mr-2">📋</span>
            View All Jobs
          </Link>
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Recent Jobs</h2>
          <Link
            to="/jobs"
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            View all
          </Link>
        </div>
        
        {recent_jobs.length === 0 ? (
          <div className="text-center py-8">
            <span className="text-4xl">📋</span>
            <p className="text-gray-500 mt-2">No jobs yet</p>
            <Link
              to="/jobs/create"
              className="inline-block mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Create your first job
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {recent_jobs.slice(0, 5).map((job) => (
              <div key={job.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-md">
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{job.service}</h3>
                  <p className="text-sm text-gray-600">{job.description}</p>
                  <p className="text-sm text-gray-500 mt-1">📍 {job.location}</p>
                </div>
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(job.status)}`}>
                    {job.status}
                  </span>
                  <Link
                    to={`/jobs/${job.id}`}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Top Fixers */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Top Rated Fixers</h2>
          <Link
            to="/fixers"
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            View all
          </Link>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {top_fixers.slice(0, 6).map((fixer) => (
            <div key={fixer.id} className="bg-gray-50 rounded-md p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-medium text-gray-900">{fixer.name}</h3>
                <div className="flex items-center space-x-1">
                  <span className="text-yellow-400">⭐</span>
                  <span className="text-sm text-gray-600">{fixer.rating.toFixed(1)}</span>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-2">📍 {fixer.location}</p>
              <div className="flex flex-wrap gap-1">
                {(() => {
                  try {
                    const services = fixer.services ? JSON.parse(fixer.services) : [];
                    return Array.isArray(services) ? services.slice(0, 3).map((service, index) => (
                      <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                        {service}
                      </span>
                    )) : [];
                  } catch (error) {
                    console.warn('Error parsing fixer services:', error, fixer.services);
                    return [];
                  }
                })()}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;