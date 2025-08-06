import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/api';

const FixerReputationDashboard = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [reputationData, setReputationData] = useState(null);
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchReputationData();
  }, []);

  const fetchReputationData = async () => {
    try {
      setLoading(true);
      
      // First, get the current user's information
      if (!user || !user.id) {
        setError(t('userNotLoggedIn', 'User not logged in. Please login first.'));
        return;
      }
      
      // Try to get fixer data directly from fixers API
      try {
        const fixersResponse = await apiService.getFixers();
        const currentUserFixer = fixersResponse.data?.find(fixer => 
          fixer.user_id === user.id || fixer.phone === user.phone
        );
        
        if (currentUserFixer?.id) {
          console.log('Found fixer ID:', currentUserFixer.id);
          // Fetch reputation data using the fixer ID
          const reputationResponse = await apiService.getFixerReputation(currentUserFixer.id);
          console.log('Reputation response:', reputationResponse);
          
          if (reputationResponse.data?.reputation) {
            setReputationData(reputationResponse.data.reputation);
          } else if (reputationResponse.data?.success) {
            // Initialize reputation if not found
            console.log('Initializing reputation for fixer:', currentUserFixer.id);
            await apiService.initializeFixerReputation(currentUserFixer.id);
            
            // Try fetching again after initialization
            const retryResponse = await apiService.getFixerReputation(currentUserFixer.id);
            if (retryResponse.data?.reputation) {
              setReputationData(retryResponse.data.reputation);
            } else {
              setError(t('reputationInitializationFailed', 'Failed to initialize reputation data. Please try again.'));
            }
          }
        } else {
          setError(t('fixerProfileNotSetup', 'Fixer profile not set up. Please complete your profile first.'));
        }
      } catch (fixerError) {
        console.error('Error getting fixer data:', fixerError);
        setError(t('errorFetchingFixerData', 'Error fetching fixer profile. Please try again.'));
      }
    } catch (err) {
      console.error('Error fetching reputation data:', err);
      setError(t('errorFetchingReputation', 'Error fetching reputation data. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  const getTierColor = (tier) => {
    switch (tier?.toLowerCase()) {
      case 'bronze':
        return 'text-amber-700 bg-amber-100 border-amber-200';
      case 'silver':
        return 'text-gray-700 bg-gray-100 border-gray-200';
      case 'gold':
        return 'text-yellow-700 bg-yellow-100 border-yellow-200';
      case 'platinum':
        return 'text-purple-700 bg-purple-100 border-purple-200';
      default:
        return 'text-gray-700 bg-gray-100 border-gray-200';
    }
  };

  const getTierIcon = (tier) => {
    switch (tier?.toLowerCase()) {
      case 'bronze':
        return '🥉';
      case 'silver':
        return '🥈';
      case 'gold':
        return '🥇';
      case 'platinum':
        return '💎';
      default:
        return '🏆';
    }
  };

  const getNextTierInfo = () => {
    const tiers = ['bronze', 'silver', 'gold', 'platinum'];
    const currentTierIndex = tiers.indexOf(reputationData?.tier?.toLowerCase() || 'bronze');
    
    if (currentTierIndex < tiers.length - 1) {
      const nextTier = tiers[currentTierIndex + 1];
      return {
        name: nextTier,
        icon: getTierIcon(nextTier),
        jobsNeeded: ((currentTierIndex + 2) * 5) - (reputationData?.stats?.jobs_completed || 0)
      };
    }
    return null;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-orange-500"></div>
        <p className="ml-4 text-lg text-gray-600">{t('loadingReputation', 'Loading reputation data...')}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="text-sm text-red-600">{error}</div>
        </div>
      </div>
    );
  }

  const nextTier = getNextTierInfo();

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {t('reputation')} {t('dashboard')}
            </h1>
            <p className="text-gray-600 mt-2">
              {t('trackReputationProgress', 'Track your reputation and progress on FixMate-SA')}
            </p>
          </div>
          <div className="text-4xl">
            {getTierIcon(reputationData?.tier)}
          </div>
        </div>
      </div>

      {/* Current Tier Status */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          {t('currentStatus', 'Current Status')}
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Current Tier */}
          <div className="text-center">
            <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium border ${getTierColor(reputationData?.tier)}`}>
              <span className="mr-2">{getTierIcon(reputationData?.tier)}</span>
              {t(`tier${reputationData?.tier?.charAt(0).toUpperCase() + reputationData?.tier?.slice(1)}`, reputationData?.tier || 'Bronze')} {t('tier', 'Tier')}
            </div>
          </div>

          {/* Overall Rating */}
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">
              {reputationData?.stats?.average_rating?.toFixed(1) || '0.0'}⭐
            </div>
            <p className="text-gray-600">{t('overallRating', 'Overall Rating')}</p>
          </div>

          {/* Jobs Completed */}
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">
              {reputationData?.stats?.jobs_completed || 0}
            </div>
            <p className="text-gray-600">{t('jobsCompleted')}</p>
          </div>
        </div>
      </div>

      {/* Progress to Next Tier */}
      {nextTier && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            {t('progressToNextTier', 'Progress to Next Tier')}
          </h2>
          
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center">
              <span className="mr-2">{nextTier.icon}</span>
              <span className="font-medium">
                {t(`tier${nextTier.name.charAt(0).toUpperCase() + nextTier.name.slice(1)}`, nextTier.name)} {t('tier', 'Tier')}
              </span>
            </div>
            <div className="text-sm text-gray-600">
              {nextTier.jobsNeeded > 0 
                ? `${nextTier.jobsNeeded} ${t('moreJobsNeeded', 'more jobs needed')}`
                : t('eligible', 'Eligible!')
              }
            </div>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-orange-600 h-2 rounded-full transition-all duration-300"
              style={{ 
                width: `${Math.min(100, ((reputationData?.stats?.jobs_completed || 0) / ((nextTier.name === 'silver' ? 10 : nextTier.name === 'gold' ? 15 : 20))) * 100)}%`
              }}
            ></div>
          </div>
        </div>
      )}

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-2xl font-bold text-green-600">
            {reputationData?.stats?.total_earned ? `R${reputationData.stats.total_earned}` : 'R0'}
          </div>
          <p className="text-gray-600">{t('totalEarnings')}</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-2xl font-bold text-purple-600">
            {reputationData?.stats?.response_rate ? `${(reputationData.stats.response_rate * 100).toFixed(0)}%` : '0%'}
          </div>
          <p className="text-gray-600">{t('responseRate', 'Response Rate')}</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-2xl font-bold text-indigo-600">
            {reputationData?.stats?.completion_rate ? `${(reputationData.stats.completion_rate * 100).toFixed(0)}%` : '0%'}
          </div>
          <p className="text-gray-600">{t('completionRate', 'Completion Rate')}</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="text-2xl font-bold text-red-600">
            {reputationData?.stats?.total_reviews || 0}
          </div>
          <p className="text-gray-600">{t('totalReviews', 'Total Reviews')}</p>
        </div>
      </div>

      {/* Recent Reviews */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          {t('recentReviews', 'Recent Reviews')}
        </h2>
        
        {reputationData?.recent_reviews && reputationData.recent_reviews.length > 0 ? (
          <div className="space-y-4">
            {reputationData.recent_reviews.map((review, index) => (
              <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <span className="text-yellow-500">
                      {'⭐'.repeat(review.rating)}
                    </span>
                    <span className="ml-2 text-sm text-gray-600">
                      {review.rating}/5
                    </span>
                  </div>
                  <span className="text-sm text-gray-500">
                    {new Date(review.created_at).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-gray-700">{review.comment}</p>
                {review.client_name && (
                  <p className="text-sm text-gray-500 mt-1">
                    - {review.client_name}
                  </p>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-4">💬</div>
            <p>{t('noReviewsYet', 'No reviews yet. Complete your first job to get reviews!')}</p>
          </div>
        )}
      </div>

      {/* Tips for Improvement */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          {t('tipsForImprovement', 'Tips for Improvement')}
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex items-start">
            <div className="text-2xl mr-3">📞</div>
            <div>
              <h3 className="font-semibold text-gray-900">{t('respondQuickly', 'Respond Quickly')}</h3>
              <p className="text-gray-600 text-sm">{t('respondQuicklyDesc', 'Reply to job requests within 30 minutes to improve your response rate.')}</p>
            </div>
          </div>

          <div className="flex items-start">
            <div className="text-2xl mr-3">✅</div>
            <div>
              <h3 className="font-semibold text-gray-900">{t('completeJobs', 'Complete Jobs')}</h3>
              <p className="text-gray-600 text-sm">{t('completeJobsDesc', 'Always complete accepted jobs to maintain a high completion rate.')}</p>
            </div>
          </div>

          <div className="flex items-start">
            <div className="text-2xl mr-3">💡</div>
            <div>
              <h3 className="font-semibold text-gray-900">{t('qualityWork', 'Quality Work')}</h3>
              <p className="text-gray-600 text-sm">{t('qualityWorkDesc', 'Deliver excellent service to receive 5-star reviews from clients.')}</p>
            </div>
          </div>

          <div className="flex items-start">
            <div className="text-2xl mr-3">📱</div>
            <div>
              <h3 className="font-semibold text-gray-900">{t('stayActive', 'Stay Active')}</h3>
              <p className="text-gray-600 text-sm">{t('stayActiveDesc', 'Keep your profile updated and availability status current.')}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FixerReputationDashboard;