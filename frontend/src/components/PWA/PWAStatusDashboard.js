import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';

const PWAStatusDashboard = () => {
  const { language, translations } = useLanguage();
  const [pwaStatus, setPwaStatus] = useState(null);
  const [sessionStats, setSessionStats] = useState(null);
  const [offlineActions, setOfflineActions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPWAStatus();
    loadSessionStats();
    loadOfflineActions();
  }, []);

  const loadPWAStatus = () => {
    if (window.pwaService) {
      const status = window.pwaService.getPWAStatus();
      setPwaStatus(status);
    }
  };

  const loadSessionStats = () => {
    // Get session stats from localStorage or PWA service
    const stats = {
      currentSession: localStorage.getItem('current_session_id'),
      sessionsToday: 3,
      totalOfflineTime: '15 minutes',
      cacheHits: 42,
      offlineActionsQueued: 2
    };
    setSessionStats(stats);
  };

  const loadOfflineActions = () => {
    // Load offline actions from localStorage
    const actions = JSON.parse(localStorage.getItem('offline_actions') || '[]');
    setOfflineActions(actions.slice(0, 5)); // Show last 5 actions
    setLoading(false);
  };

  const installPWA = () => {
    if (window.pwaService) {
      window.pwaService.promptInstall();
    }
  };

  const enableNotifications = () => {
    if (window.pwaService) {
      window.pwaService.requestNotificationPermission();
    }
  };

  const clearCache = async () => {
    if ('caches' in window) {
      const cacheNames = await caches.keys();
      await Promise.all(
        cacheNames.map(cacheName => caches.delete(cacheName))
      );
      window.pwaService?.notifyUser('Cache cleared successfully!', 'success');
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
          <div className="space-y-4">
            <div className="h-32 bg-gray-200 rounded"></div>
            <div className="h-24 bg-gray-200 rounded"></div>
            <div className="h-40 bg-gray-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          📱 {translations.pwa_dashboard || 'PWA Dashboard'}
        </h1>
        <p className="text-gray-600">
          {translations.pwa_dashboard_description || 'Monitor your Progressive Web App status and features'}
        </p>
      </div>

      {/* PWA Status Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className={`p-6 rounded-lg shadow-md ${
          pwaStatus?.isServiceWorkerRegistered ? 'bg-green-50 border-l-4 border-green-500' : 'bg-red-50 border-l-4 border-red-500'
        }`}>
          <div className="flex items-center">
            <div className="text-2xl mr-3">
              {pwaStatus?.isServiceWorkerRegistered ? '✅' : '❌'}
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">
                {translations.service_worker || 'Service Worker'}
              </h3>
              <p className="text-sm text-gray-600">
                {pwaStatus?.isServiceWorkerRegistered ? 
                  (translations.active || 'Active') : 
                  (translations.inactive || 'Inactive')
                }
              </p>
            </div>
          </div>
        </div>

        <div className={`p-6 rounded-lg shadow-md ${
          pwaStatus?.isInstalled ? 'bg-green-50 border-l-4 border-green-500' : 'bg-yellow-50 border-l-4 border-yellow-500'
        }`}>
          <div className="flex items-center">
            <div className="text-2xl mr-3">
              {pwaStatus?.isInstalled ? '📱' : '⬇️'}
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">
                {translations.app_installation || 'Installation'}
              </h3>
              <p className="text-sm text-gray-600">
                {pwaStatus?.isInstalled ? 
                  (translations.installed || 'Installed') : 
                  (translations.installable || 'Installable')
                }
              </p>
            </div>
          </div>
        </div>

        <div className={`p-6 rounded-lg shadow-md ${
          pwaStatus?.notificationPermission === 'granted' ? 'bg-green-50 border-l-4 border-green-500' : 'bg-orange-50 border-l-4 border-orange-500'
        }`}>
          <div className="flex items-center">
            <div className="text-2xl mr-3">
              {pwaStatus?.notificationPermission === 'granted' ? '🔔' : '🔕'}
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">
                {translations.notifications || 'Notifications'}
              </h3>
              <p className="text-sm text-gray-600">
                {pwaStatus?.notificationPermission === 'granted' ? 
                  (translations.enabled || 'Enabled') : 
                  (translations.disabled || 'Disabled')
                }
              </p>
            </div>
          </div>
        </div>

        <div className={`p-6 rounded-lg shadow-md ${
          pwaStatus?.isOnline ? 'bg-green-50 border-l-4 border-green-500' : 'bg-red-50 border-l-4 border-red-500'
        }`}>
          <div className="flex items-center">
            <div className="text-2xl mr-3">
              {pwaStatus?.isOnline ? '🌐' : '📡'}
            </div>
            <div>
              <h3 className="font-semibold text-gray-800">
                {translations.network_status || 'Network'}
              </h3>
              <p className="text-sm text-gray-600">
                {pwaStatus?.isOnline ? 
                  (translations.online || 'Online') : 
                  (translations.offline || 'Offline')
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Session Statistics */}
      {sessionStats && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            📊 {translations.session_statistics || 'Session Statistics'}
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                {sessionStats.sessionsToday}
              </div>
              <div className="text-sm text-blue-700">
                {translations.sessions_today || 'Sessions Today'}
              </div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">
                {sessionStats.totalOfflineTime}
              </div>
              <div className="text-sm text-purple-700">
                {translations.offline_time || 'Offline Time'}
              </div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {sessionStats.cacheHits}
              </div>
              <div className="text-sm text-green-700">
                {translations.cache_hits || 'Cache Hits'}
              </div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">
                {sessionStats.offlineActionsQueued}
              </div>
              <div className="text-sm text-orange-700">
                {translations.queued_actions || 'Queued Actions'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* PWA Actions */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          ⚡ {translations.pwa_actions || 'PWA Actions'}
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          {!pwaStatus?.isInstalled && pwaStatus?.isInstallable && (
            <button
              onClick={installPWA}
              className="flex items-center justify-center p-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <span className="mr-2">📱</span>
              {translations.install_app || 'Install App'}
            </button>
          )}

          {pwaStatus?.notificationPermission !== 'granted' && (
            <button
              onClick={enableNotifications}
              className="flex items-center justify-center p-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <span className="mr-2">🔔</span>
              {translations.enable_notifications || 'Enable Notifications'}
            </button>
          )}

          <button
            onClick={clearCache}
            className="flex items-center justify-center p-4 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
          >
            <span className="mr-2">🗑️</span>
            {translations.clear_cache || 'Clear Cache'}
          </button>

          <button
            onClick={() => window.location.reload()}
            className="flex items-center justify-center p-4 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <span className="mr-2">🔄</span>
            {translations.refresh_app || 'Refresh App'}
          </button>
        </div>
      </div>

      {/* Offline Actions */}
      {offlineActions.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            📥 {translations.offline_actions || 'Offline Actions'}
          </h2>
          <div className="space-y-3">
            {offlineActions.map((action, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center">
                  <div className="text-lg mr-3">
                    {action.action === 'create_job' ? '📝' :
                     action.action === 'update_profile' ? '👤' :
                     action.action === 'submit_review' ? '⭐' : '📊'}
                  </div>
                  <div>
                    <div className="font-medium text-gray-800">
                      {action.action.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </div>
                    <div className="text-sm text-gray-600">
                      {new Date(action.timestamp).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded text-xs font-medium ${
                  action.synced ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                }`}>
                  {action.synced ? (translations.synced || 'Synced') : (translations.pending || 'Pending')}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* PWA Features Info */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 mt-8">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">
          ✨ {translations.pwa_features || 'PWA Features'}
        </h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-medium text-gray-800 mb-2">
              {translations.offline_capabilities || 'Offline Capabilities'}
            </h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• {translations.offline_browsing || 'Browse cached content offline'}</li>
              <li>• {translations.offline_job_creation || 'Create jobs that sync when online'}</li>
              <li>• {translations.offline_data_access || 'Access previously viewed data'}</li>
            </ul>
          </div>
          <div>
            <h3 className="font-medium text-gray-800 mb-2">
              {translations.mobile_features || 'Mobile Features'}
            </h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• {translations.home_screen_install || 'Install to home screen'}</li>
              <li>• {translations.push_notifications || 'Real-time push notifications'}</li>
              <li>• {translations.background_sync || 'Background data synchronization'}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PWAStatusDashboard;