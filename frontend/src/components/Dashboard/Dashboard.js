import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/api';
import { Link, useNavigate } from 'react-router-dom';
import Logo from '../Common/Logo';
import AnnouncementDisplay from '../Common/AnnouncementDisplay';

const Dashboard = () => {
  const { user, getUserRole } = useAuth();
  const { t } = useLanguage();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);
  const navigate = useNavigate();

  const userRole = getUserRole();

  const fetchDashboardData = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      console.log('Dashboard: Fetching data for user:', user);
      const response = await apiService.getDashboard(user.id);
      console.log('Dashboard: API response:', response);
      setDashboardData(response.data);
      setLastUpdated(new Date());
      setError(''); // Clear any previous errors
    } catch (err) {
      console.error('Dashboard: Error fetching dashboard:', err);
      console.error('Dashboard: Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      });
      setError(`Failed to load dashboard data: ${err.response?.data?.detail || err.message}`);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.id) {
      console.log('Dashboard: User found, fetching data...');
      fetchDashboardData();
    } else {
      console.log('Dashboard: No user ID found:', user);
      setLoading(false);
      setError('User not found');
    }
  }, [user]);

  // Auto-refresh dashboard data every 30 seconds
  useEffect(() => {
    if (!user?.id) return;

    const refreshInterval = setInterval(() => {
      console.log('Dashboard: Auto-refreshing data...');
      fetchDashboardData(false); // Don't show loading spinner for auto-refresh
    }, 30000); // 30 seconds

    return () => clearInterval(refreshInterval);
  }, [user?.id]);

  // Refresh when user comes back to the tab (visibility change)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden && user?.id) {
        console.log('Dashboard: Tab became visible, refreshing data...');
        fetchDashboardData(false);
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, [user?.id]);

  // Refresh when navigating back to dashboard (e.g., from job creation)
  useEffect(() => {
    const handleFocus = () => {
      if (user?.id) {
        console.log('Dashboard: Window gained focus, refreshing data...');
        fetchDashboardData(false);
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [user?.id]);

  // Storage event listener for cross-tab updates
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === 'fixmate_dashboard_refresh' && user?.id) {
        console.log('Dashboard: Storage event detected, refreshing data...');
        fetchDashboardData(false);
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [user?.id]);

  // Manual refresh function
  const handleRefresh = () => {
    console.log('Dashboard: Manual refresh triggered');
    fetchDashboardData(true);
  };

  const getRoleBasedContent = () => {
    switch (userRole) {
      case 'client':
        return {
          title: t('dashboard') + ' - ' + t('client', 'Client'),
          subtitle: t('manageServiceRequests', 'Manage your service requests and connect with trusted fixers'),
          quickActions: [
            { 
              title: t('createJob'), 
              desc: t('postNewServiceRequest', 'Post a new service request'), 
              path: '/jobs/create', 
              icon: '➕',
              color: 'bg-blue-600 hover:bg-blue-700'
            },
            { 
              title: t('findFixers'), 
              desc: t('browseServiceProviders', 'Browse available service providers'), 
              path: '/fixers', 
              icon: '🔧',
              color: 'bg-orange-600 hover:bg-orange-700'
            },
            { 
              title: t('businessCompliance', 'Business Compliance'), 
              desc: t('businessComplianceDesc', 'Company registration, tax compliance, legal documentation'), 
              path: '/client/business-compliance', 
              icon: '🏢',
              color: 'bg-green-600 hover:bg-green-700'
            },
            { 
              title: t('enterprisePortal', 'Enterprise Portal'), 
              desc: t('enterprisePortalDesc', 'Bulk bookings, contracts, analytics, team management'), 
              path: '/client/enterprise', 
              icon: '🏢',
              color: 'bg-gray-800 hover:bg-gray-900'
            },
            { 
              title: t('myJobs', 'My Jobs'), 
              desc: t('viewJobRequests', 'View your job requests'), 
              path: '/jobs/list', 
              icon: '📋',
              color: 'bg-purple-600 hover:bg-purple-700'
            },
            { 
              title: t('rateCompletedJobs', 'Rate Completed Jobs'), 
              desc: t('rateFixerExperiences', 'Rate your fixer experiences'), 
              path: '/client/rate-jobs', 
              icon: '⭐',
              color: 'bg-yellow-600 hover:bg-yellow-700'
            }
          ],
          stats: [
            { label: t('activeJobs'), value: dashboardData?.stats?.active_jobs || 0, icon: '🔄' },
            { label: t('completedJobs'), value: dashboardData?.stats?.completed_jobs || 0, icon: '✅' },
            { label: t('totalSpent', 'Total Spent'), value: `R${dashboardData?.stats?.total_spent || 0}`, icon: '💰' },
            { label: t('pendingJobs', 'Pending Jobs'), value: dashboardData?.stats?.pending_jobs || 0, icon: '⏳' }
          ]
        };
      case 'fixer':
        return {
          title: t('dashboard') + ' - ' + t('fixer', 'Fixer'),
          subtitle: t('manageJobsGrowBusiness', 'Manage your jobs and grow your service business'),
          quickActions: [
            { 
              title: t('availableJobs'), 
              desc: t('browseAcceptJobs', 'Browse and accept new jobs'), 
              path: '/fixer/jobs', 
              icon: '🔨',
              color: 'bg-orange-600 hover:bg-orange-700'
            },
            { 
              title: t('businessSetup', 'Business Setup'), 
              desc: t('businessSetupDesc', 'Professional licensing, business registration, compliance'), 
              path: '/fixer/business-compliance', 
              icon: '📋',
              color: 'bg-green-600 hover:bg-green-700'
            },
            { 
              title: t('myPayments', 'My Payments'), 
              desc: t('trackEarningsPayments', 'Track earnings and payments'), 
              path: '/fixer/payment', 
              icon: '💳',
              color: 'bg-blue-600 hover:bg-blue-700'
            },
            { 
              title: t('reputation'), 
              desc: t('viewReputationScore', 'View your reputation score'), 
              path: '/fixer/reputation', 
              icon: '⭐',
              color: 'bg-yellow-600 hover:bg-yellow-700'
            },
            { 
              title: t('learningCenter', 'Learning Center'), 
              desc: t('improveSkills', 'Improve your skills'), 
              path: '/fixer/learning', 
              icon: '🎓',
              color: 'bg-purple-600 hover:bg-purple-700'
            }
          ],
          stats: [
            { label: t('jobsCompleted'), value: dashboardData?.stats?.jobs_completed || 0, icon: '✅' },
            { label: t('currentRating', 'Current Rating'), value: dashboardData?.stats?.rating || '5.0', icon: '⭐' },
            { label: t('totalEarnings'), value: `R${dashboardData?.stats?.total_earned || 0}`, icon: '💰' },
            { label: t('activeJobs'), value: dashboardData?.stats?.active_jobs || 0, icon: '🔄' }
          ]
        };
      case 'admin':
        return {
          title: t('dashboard') + ' - ' + t('admin', 'Admin'),
          subtitle: t('managePlatformOperations', 'Manage the FixMate-SA platform and monitor operations'),
          quickActions: [
            { 
              title: t('adminPanel'), 
              desc: t('platformManagementTools', 'Platform management tools'), 
              path: '/admin/panel', 
              icon: '⚙️',
              color: 'bg-red-600 hover:bg-red-700'
            },
            { 
              title: t('smartMatching', 'Smart Matching'), 
              desc: t('viewMatchingAnalytics', 'View matching analytics'), 
              path: '/admin/smart-matching', 
              icon: '🎯',
              color: 'bg-indigo-600 hover:bg-indigo-700'
            },
            { 
              title: t('photoVerification', 'Photo Verification'), 
              desc: t('reviewFixerPhotos', 'Review fixer photos'), 
              path: '/admin/photo-verification', 
              icon: '📸',
              color: 'bg-blue-600 hover:bg-blue-700'
            },
            { 
              title: t('businessTools', 'Business Tools'), 
              desc: t('businessComplianceFeatures', 'Business compliance features'), 
              path: '/admin/business-compliance', 
              icon: '🏢',
              color: 'bg-gray-600 hover:bg-gray-700'
            }
          ],
          stats: [
            { label: t('totalUsers', 'Total Users'), value: dashboardData?.stats?.total_users || 0, icon: '👥' },
            { label: t('activeJobs'), value: dashboardData?.stats?.total_active_jobs || 0, icon: '🔄' },
            { label: t('platformRevenue', 'Platform Revenue'), value: `R${dashboardData?.stats?.platform_revenue || 0}`, icon: '💰' },
            { label: t('successRate', 'Success Rate'), value: `${dashboardData?.stats?.success_rate || 0}%`, icon: '📈' }
          ]
        };
      default:
        return {
          title: t('dashboard'),
          subtitle: t('welcomeMessage'),
          quickActions: [],
          stats: []
        };
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>{t('loading')}</p>
      </div>
    );
  }

  const content = getRoleBasedContent();

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <div className="dashboard-card">
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <h1 className="dashboard-title">{content.title}</h1>
            <p className="dashboard-subtitle">{content.subtitle}</p>
          </div>
          <div className="flex items-center space-x-3">
            {lastUpdated && (
              <div className="text-sm text-gray-500">
                <span className="hidden sm:inline">{t('lastUpdated', 'Last updated')}: </span>
                <span>{lastUpdated.toLocaleTimeString()}</span>
              </div>
            )}
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-100 hover:bg-blue-200 disabled:bg-gray-100 disabled:cursor-not-allowed text-blue-700 disabled:text-gray-400 rounded-lg transition-colors duration-200"
              title={t('refreshData', 'Refresh data')}
            >
              <span className={`text-lg ${loading ? 'animate-spin' : ''}`}>
                {loading ? '🔄' : '↻'}
              </span>
              <span className="hidden sm:inline text-sm font-medium">
                {loading ? t('updating', 'Updating...') : t('refresh', 'Refresh')}
              </span>
            </button>
          </div>
        </div>
        
        {error && (
          <div className="alert alert-error mt-4">
            <strong>{t('error')}:</strong> {error}
            <button 
              onClick={handleRefresh}
              className="ml-3 text-sm underline hover:no-underline"
            >
              {t('tryAgain', 'Try again')}
            </button>
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

      {/* Announcements Section */}
      <div className="dashboard-card">
        <AnnouncementDisplay />
      </div>

      {/* Quick Actions */}
      {content.quickActions.length > 0 && (
        <div className="dashboard-card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('quickActions')}</h2>
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
        <h2 className="text-lg font-semibold text-gray-900 mb-4">{t('recentActivity')}</h2>
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
            <p className="text-gray-500">{t('noRecentActivity', 'No recent activity to display')}</p>
            <p className="text-sm text-gray-400 mt-2">{t('startUsingFixMate', 'Start using FixMate-SA to see your activity here')}</p>
          </div>
        )}
      </div>

      {/* Welcome Card for New Users */}
      {!dashboardData?.has_activity && (
        <div className="dashboard-card bg-gradient-to-r from-blue-50 to-green-50 border-blue-200">
          <div className="text-center py-6">
            <span className="text-5xl mb-4 block">🎉</span>
            <h2 className="text-xl font-bold text-gray-900 mb-2">{t('welcomeMessage', 'Welcome to FixMate-SA!')}</h2>
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