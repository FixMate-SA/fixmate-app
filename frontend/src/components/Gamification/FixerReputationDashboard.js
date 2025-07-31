import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import api from '../../services/api';

const FixerReputationDashboard = ({ fixerId }) => {
  const { user } = useAuth();
  const { language, translations } = useLanguage();
  const [reputationData, setReputationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showInitialize, setShowInitialize] = useState(false);

  // Fetch reputation data
  const fetchReputationData = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/fixer/${fixerId}/reputation`);
      
      if (response.data.success) {
        setReputationData(response.data.reputation);
        setShowInitialize(false);
      } else {
        setShowInitialize(true);
      }
    } catch (err) {
      if (err.response?.status === 404) {
        setShowInitialize(true);
      } else {
        setError(err.response?.data?.detail || 'Failed to fetch reputation data');
      }
    } finally {
      setLoading(false);
    }
  };

  // Initialize reputation
  const initializeReputation = async () => {
    try {
      const response = await api.post(`/fixer/${fixerId}/reputation/initialize`);
      
      if (response.data.success) {
        await fetchReputationData();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to initialize reputation');
    }
  };

  // Get tier color
  const getTierColor = (tier) => {
    const colors = {
      'bronze': 'text-orange-600 bg-orange-100',
      'silver': 'text-gray-600 bg-gray-100',
      'gold': 'text-yellow-600 bg-yellow-100',
      'platinum': 'text-purple-600 bg-purple-100',
      'diamond': 'text-blue-600 bg-blue-100'
    };
    return colors[tier?.toLowerCase()] || 'text-gray-600 bg-gray-100';
  };

  // Get tier icon
  const getTierIcon = (tier) => {
    const icons = {
      'bronze': '🥉',
      'silver': '🥈',
      'gold': '🥇',
      'platinum': '⭐',
      'diamond': '💎'
    };
    return icons[tier?.toLowerCase()] || '🏆';
  };

  // Calculate progress to next tier
  const getNextTierProgress = (currentPoints, currentTier) => {
    const tierThresholds = {
      'bronze': { next: 'silver', points: 1000 },
      'silver': { next: 'gold', points: 2500 },
      'gold': { next: 'platinum', points: 5000 },
      'platinum': { next: 'diamond', points: 10000 },
      'diamond': { next: null, points: null }
    };

    const current = tierThresholds[currentTier?.toLowerCase()];
    if (!current || !current.next) return null;

    const progress = (currentPoints / current.points) * 100;
    return {
      nextTier: current.next,
      progress: Math.min(progress, 100),
      pointsNeeded: Math.max(0, current.points - currentPoints)
    };
  };

  useEffect(() => {
    if (fixerId) {
      fetchReputationData();
    }
  }, [fixerId]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="space-y-4">
            <div className="h-20 bg-gray-200 rounded"></div>
            <div className="h-16 bg-gray-200 rounded"></div>
            <div className="h-24 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">
          {translations.reputation_dashboard || 'Reputation Dashboard'}
        </h3>
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      </div>
    );
  }

  if (showInitialize) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">
          {translations.reputation_dashboard || 'Reputation Dashboard'}
        </h3>
        <div className="text-center py-8">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
          </div>
          <h4 className="text-lg font-medium text-gray-800 mb-2">
            {translations.reputation_not_initialized || 'Reputation System Not Initialized'}
          </h4>
          <p className="text-gray-600 mb-4">
            {translations.reputation_init_description || 'Start your journey to earn badges, climb tiers, and build your professional reputation.'}
          </p>
          <button
            onClick={initializeReputation}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
          >
            {translations.initialize_reputation || 'Initialize Reputation'}
          </button>
        </div>
      </div>
    );
  }

  if (!reputationData) return null;

  const nextTierInfo = getNextTierProgress(reputationData.tier_points, reputationData.current_tier);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold text-gray-800 mb-6">
        {translations.reputation_dashboard || 'Reputation Dashboard'}
      </h3>

      <div className="space-y-6">
        {/* Current Tier */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-lg font-semibold text-gray-800 mb-2">
                {translations.current_tier || 'Current Tier'}
              </h4>
              <div className={`inline-flex items-center px-4 py-2 rounded-full text-lg font-bold ${getTierColor(reputationData.current_tier)}`}>
                <span className="text-2xl mr-2">{getTierIcon(reputationData.current_tier)}</span>
                {reputationData.current_tier?.toUpperCase() || 'BRONZE'}
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-600 mb-1">
                {translations.tier_points || 'Tier Points'}
              </div>
              <div className="text-3xl font-bold text-gray-800">
                {reputationData.tier_points || 0}
              </div>
            </div>
          </div>
        </div>

        {/* Progress to Next Tier */}
        {nextTierInfo && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-700">
                {translations.progress_to || 'Progress to'} {nextTierInfo.nextTier?.toUpperCase()}
              </span>
              <span className="text-sm text-gray-600">
                {nextTierInfo.pointsNeeded} {translations.points_needed || 'points needed'}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${nextTierInfo.progress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Performance Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {reputationData.client_satisfaction_avg?.toFixed(1) || '0.0'}
            </div>
            <div className="text-xs text-green-700 font-medium">
              {translations.satisfaction || 'Satisfaction'}
            </div>
          </div>

          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {reputationData.jobs_completed || 0}
            </div>
            <div className="text-xs text-blue-700 font-medium">
              {translations.jobs_completed || 'Jobs Done'}
            </div>
          </div>

          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {reputationData.streak_count || 0}
            </div>
            <div className="text-xs text-purple-700 font-medium">
              {translations.current_streak || 'Streak'}
            </div>
          </div>

          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {reputationData.on_time_percentage?.toFixed(0) || 0}%
            </div>
            <div className="text-xs text-orange-700 font-medium">
              {translations.on_time || 'On Time'}
            </div>
          </div>
        </div>

        {/* Recent Achievements */}
        {reputationData.recent_achievements && reputationData.recent_achievements.length > 0 && (
          <div>
            <h4 className="text-lg font-semibold text-gray-800 mb-3">
              {translations.recent_achievements || 'Recent Achievements'}
            </h4>
            <div className="space-y-2">
              {reputationData.recent_achievements.map((achievement, index) => (
                <div key={index} className="flex items-center p-3 bg-yellow-50 rounded-lg">
                  <span className="text-xl mr-3">🏆</span>
                  <div>
                    <div className="font-medium text-gray-800">{achievement.title}</div>
                    <div className="text-sm text-gray-600">{achievement.description}</div>
                  </div>
                  <div className="ml-auto text-xs text-gray-500">
                    +{achievement.points || 0} pts
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-3 pt-4 border-t">
          <button
            onClick={() => window.location.href = '/fixers/leaderboard'}
            className="flex-1 bg-gray-100 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-200 transition-colors"
          >
            {translations.view_leaderboard || 'View Leaderboard'}
          </button>
          <button
            onClick={() => window.location.href = '/fixer/achievements'}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
          >
            {translations.view_achievements || 'View All Achievements'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default FixerReputationDashboard;