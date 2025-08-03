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
            { label: 'Completed Jobs', value: dashboardData?.stats?.completed_jobs || 0, icon: '✅' },
            { label: 'Total Spent', value: `R${dashboardData?.stats?.total_spent || 0}`, icon: '💰' },
            { label: 'Pending Jobs', value: dashboardData?.stats?.pending_jobs || 0, icon: '⏳' }
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
              color: 'bg-orange-600 hover:bg-orange-700'
            },
            { 
              title: 'My Payments', 
              desc: 'Track earnings and payments', 
              path: '/fixer/payment', 
              icon: '💳',
              color: 'bg-blue-600 hover:bg-blue-700'
            },
            { 
              title: 'Reputation', 
              desc: 'View your reputation score', 
              path: '/fixer/reputation', 
              icon: '⭐',
              color: 'bg-yellow-600 hover:bg-yellow-700'
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
            { label: 'Current Rating', value: dashboardData?.stats?.rating || '5.0', icon: '⭐' },
            { label: 'Total Earned', value: `R${dashboardData?.stats?.total_earned || 0}`, icon: '💰' },
            { label: 'Active Jobs', value: dashboardData?.stats?.active_jobs || 0, icon: '🔄' }
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
              title: 'Photo Verification', 
              desc: 'Review fixer photos', 
              path: '/admin/photo-verification', 
              icon: '📸',
              color: 'bg-blue-600 hover:bg-blue-700'
            },
            { 
              title: 'Business Tools', 
              desc: 'Business compliance features', 
              path: '/admin/business-compliance', 
              icon: '🏢',
              color: 'bg-gray-600 hover:bg-gray-700'
            }
          ],
          stats: [
            { label: 'Total Users', value: dashboardData?.stats?.total_users || 0, icon: '👥' },
            { label: 'Active Jobs', value: dashboardData?.stats?.total_active_jobs || 0, icon: '🔄' },
            { label: 'Platform Revenue', value: `R${dashboardData?.stats?.platform_revenue || 0}`, icon: '💰' },
            { label: 'Success Rate', value: `${dashboardData?.stats?.success_rate || 0}%`, icon: '📈' }
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

  const content = getRoleBasedContent();

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="dashboard-card">
        <h1 className="dashboard-title">{content.title}</h1>
        <p className="dashboard-subtitle">{content.subtitle}</p>
        
        {error && (
          <div className="alert alert-error">
            <strong>Error:</strong> {error}
          </div>
        )}
      </div>

      {/* Stats Section */}
      {content.stats.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {content.stats.map((stat, index) => (
            <div key={index} className="stat-card">
              <span className="text-2xl mb-2 block">{stat.icon}</span>
              <span className="stat-number">{stat.value}</span>
              <span className="stat-label">{stat.label}</span>
            </div>
          ))}
        </div>
      )}

      {/* Quick Actions */}
      {content.quickActions.length > 0 && (
        <div className="dashboard-card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {content.quickActions.map((action, index) => (
              <button
                key={index}
                onClick={() => navigate(action.path)}
                className={`
                  p-4 rounded-lg text-left transition-all duration-200 transform hover:scale-105 text-white
                  ${action.color}
                `}
              >
                <div className="flex items-center space-x-3 mb-2">
                  <span className="text-2xl">{action.icon}</span>
                  <h3 className="font-semibold">{action.title}</h3>
                </div>
                <p className="text-sm opacity-90">{action.desc}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity */}
      <div className="dashboard-card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        {dashboardData?.recent_activity?.length > 0 ? (
          <div className="space-y-3">
            {dashboardData.recent_activity.slice(0, 5).map((activity, index) => (
              <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <span className="text-blue-600 text-sm">📋</span>
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                  <p className="text-xs text-gray-500">{activity.timestamp}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <span className="text-4xl mb-4 block">📊</span>
            <p className="text-gray-500">No recent activity to display</p>
            <p className="text-sm text-gray-400 mt-2">Start using FixMate-SA to see your activity here</p>
          </div>
        )}
      </div>

      {/* Welcome Card for New Users */}
      {!dashboardData?.has_activity && (
        <div className="dashboard-card bg-gradient-to-r from-blue-50 to-green-50 border-blue-200">
          <div className="text-center py-6">
            <span className="text-5xl mb-4 block">🎉</span>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Welcome to FixMate-SA!</h2>
            <p className="text-gray-600 mb-4">
              {userRole === 'client' && "Start creating jobs and connecting with trusted fixers."}
              {userRole === 'fixer' && "Begin accepting jobs and growing your service business."}
              {userRole === 'admin' && "Manage the platform and monitor operations."}
            </p>
            {content.quickActions.length > 0 && (
              <button
                onClick={() => navigate(content.quickActions[0].path)}
                className="action-button"
              >
                Get Started
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;