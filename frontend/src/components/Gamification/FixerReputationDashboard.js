import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';

const FixerReputationDashboard = () => {
  const { user } = useAuth();
  const [reputationData, setReputationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fixerId = user?.id;

  useEffect(() => {
    if (fixerId) {
      fetchReputationData();
    }
  }, [fixerId]);

  const fetchReputationData = async () => {
    try {
      setLoading(true);
      setError('');
      
      let response;
      try {
        response = await apiService.getDashboard(fixerId);
      } catch (err) {
        response = { data: { stats: {} } };
      }
      
      const mockReputationData = {
        current_tier: 'Expert',
        current_score: response.data?.stats?.rating || 4.8,
        jobs_completed: response.data?.stats?.jobs_completed || 0,
        success_rate: response.data?.stats?.success_rate || 95,
        total_earnings: response.data?.stats?.total_earned || 0,
        client_reviews: response.data?.stats?.total_reviews || 0,
        badges: [
          { name: 'Reliable Worker', icon: '🎯', earned: true },
          { name: 'Quality Expert', icon: '⭐', earned: true },
          { name: 'Fast Response', icon: '⚡', earned: true },
          { name: 'Customer Favorite', icon: '❤️', earned: false }
        ],
        recent_achievements: [
          'Completed 10+ jobs this month',
          'Maintained 4.8+ rating',
          'Quick response time under 2 hours'
        ]
      };
      
      setReputationData(mockReputationData);
    } catch (err) {
      console.error('Error fetching reputation data:', err);
      setError('Unable to load reputation data. Please try again later.');
    } finally {
      setLoading(false);
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
      <div className="dashboard-card">
        <div className="alert alert-error">
          <strong>Error:</strong> {error}
        </div>
      </div>
    );
  }

  if (!reputationData) {
    return (
      <div className="dashboard-card">
        <div className="text-center py-8">
          <span className="text-4xl mb-4 block">⭐</span>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Reputation Dashboard</h2>
          <p className="text-gray-600 mb-4">
            Complete more jobs to build your reputation and unlock achievements!
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="dashboard-card">
        <h1 className="dashboard-title">Fixer Reputation Dashboard</h1>
        <p className="dashboard-subtitle">Track your reputation, achievements, and performance metrics</p>
      </div>

      <div className="dashboard-card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Status</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="stat-card">
            <span className="text-2xl mb-2 block">🏆</span>
            <span className="stat-number">{reputationData.current_tier}</span>
            <span className="stat-label">Current Tier</span>
          </div>
          <div className="stat-card">
            <span className="text-2xl mb-2 block">⭐</span>
            <span className="stat-number">{reputationData.current_score}</span>
            <span className="stat-label">Rating Score</span>
          </div>
          <div className="stat-card">
            <span className="text-2xl mb-2 block">✅</span>
            <span className="stat-number">{reputationData.jobs_completed}</span>
            <span className="stat-label">Jobs Completed</span>
          </div>
          <div className="stat-card">
            <span className="text-2xl mb-2 block">📈</span>
            <span className="stat-number">{reputationData.success_rate}%</span>
            <span className="stat-label">Success Rate</span>
          </div>
        </div>
      </div>

      <div className="dashboard-card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Badges & Achievements</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
          {reputationData.badges.map((badge, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg text-center transition-all duration-200 ${
                badge.earned 
                  ? 'bg-orange-50 border-2 border-orange-200' 
                  : 'bg-gray-50 border-2 border-gray-200 opacity-50'
              }`}
            >
              <div className="text-3xl mb-2">{badge.icon}</div>
              <div className={`text-sm font-medium ${badge.earned ? 'text-orange-800' : 'text-gray-500'}`}>
                {badge.name}
              </div>
              {badge.earned && (
                <div className="text-xs text-green-600 mt-1">✅ Earned</div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="dashboard-card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Achievements</h2>
        <div className="space-y-3">
          {reputationData.recent_achievements.map((achievement, index) => (
            <div key={index} className="flex items-center space-x-3 p-3 bg-green-50 rounded-lg">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 text-sm">🎉</span>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{achievement}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="dashboard-card">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Performance Summary</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-blue-600 text-2xl mb-2">💰</div>
            <div className="text-blue-900 font-semibold">R{reputationData.total_earnings}</div>
            <div className="text-blue-600 text-sm">Total Earnings</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-purple-600 text-2xl mb-2">📝</div>
            <div className="text-purple-900 font-semibold">{reputationData.client_reviews}</div>
            <div className="text-purple-600 text-sm">Client Reviews</div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="text-orange-600 text-2xl mb-2">🔥</div>
            <div className="text-orange-900 font-semibold">Active</div>
            <div className="text-orange-600 text-sm">Current Status</div>
          </div>
        </div>
      </div>

      <div className="dashboard-card bg-gradient-to-r from-blue-50 to-green-50 border-blue-200">
        <div className="text-center py-6">
          <span className="text-4xl mb-4 block">🚀</span>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Keep Growing!</h2>
          <p className="text-gray-600 mb-4">
            Complete more jobs, maintain high quality, and respond quickly to improve your reputation.
          </p>
          <div className="text-sm text-gray-500 space-y-1">
            <p>• Aim for 5-star ratings on every job</p>
            <p>• Respond to job requests within 2 hours</p>
            <p>• Upload quality before/after photos</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FixerReputationDashboard;