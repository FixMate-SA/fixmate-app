import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/api';
import LanguageSelector from '../Common/LanguageSelector';
import PushNotificationManager from '../PushNotifications/PushNotificationManager';
import ClientProfile from './ClientProfile';
import FixerProfile from './FixerProfile';
import AdminProfile from './AdminProfile';

const Profile = () => {
  const { user, getUserRole } = useAuth();
  const { t } = useLanguage();
  const [userProfile, setUserProfile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchUserProfile = async () => {
    if (!user?.id) return;
    
    setIsLoading(true);
    try {
      const response = await apiService.getProfile(user.id);
      if (response.data.success) {
        setUserProfile(response.data.user);
      } else {
        setError('Failed to load profile');
      }
    } catch (error) {
      console.error('Profile fetch error:', error);
      setError('Failed to load profile data');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUserProfile();
  }, [user?.id]);

  const handleProfileUpdate = () => {
    // Refresh profile data after update
    fetchUserProfile();
  };

  const renderRoleSpecificProfile = () => {
    const userRole = getUserRole();
    
    switch (userRole) {
      case 'client':
        return (
          <ClientProfile 
            userProfile={userProfile} 
            onUpdateProfile={handleProfileUpdate}
          />
        );
      case 'fixer':
        return (
          <FixerProfile 
            userProfile={userProfile} 
            onUpdateProfile={handleProfileUpdate}
          />
        );
      case 'admin':
        return (
          <AdminProfile 
            userProfile={userProfile} 
            onUpdateProfile={handleProfileUpdate}
          />
        );
      default:
        return (
          <ClientProfile 
            userProfile={userProfile} 
            onUpdateProfile={handleProfileUpdate}
          />
        );
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <p className="text-red-800">{error}</p>
          <button 
            onClick={fetchUserProfile}
            className="mt-2 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
        <div className="border-b border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                <span className="text-xl text-orange-600">👤</span>
              </div>
            </div>
            <div className="ml-4">
              <h1 className="text-2xl font-bold text-gray-900">
                {t('profileSettings', 'Profile Settings')}
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {t('manageProfileInfo', 'Manage your account information and preferences')}
              </p>
            </div>
          </div>
        </div>
        
        <div className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                {userProfile?.first_name} {userProfile?.last_name}
              </h2>
              <p className="text-sm text-gray-600">
                {userProfile?.role} • {userProfile?.email}
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <LanguageSelector />
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                userProfile?.role === 'admin' ? 'bg-blue-100 text-blue-800' :
                userProfile?.role === 'fixer' ? 'bg-green-100 text-green-800' :
                'bg-orange-100 text-orange-800'
              }`}>
                {userProfile?.role?.charAt(0)?.toUpperCase() + userProfile?.role?.slice(1)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Role-specific Profile Components */}
      {renderRoleSpecificProfile()}

      {/* Push Notifications Section */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 mt-6">
        <div className="border-b border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center">
                <span className="text-xl text-orange-600">🔔</span>
              </div>
            </div>
            <div className="ml-4">
              <h2 className="text-xl font-semibold text-gray-900">
                {t('notificationSettings', 'Notification Settings')}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {t('manageNotifications', 'Manage your push notification preferences')}
              </p>
            </div>
          </div>
        </div>
        
        <div className="p-6">
          <PushNotificationManager />
        </div>
      </div>
    </div>
  );
};

export default Profile;