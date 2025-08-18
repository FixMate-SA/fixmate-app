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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [profileData, setProfileData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    phone: user?.phone || '',
    location: user?.location || '',
    bio: user?.bio || '',
    skills: user?.skills || [],
    experience_years: user?.experience_years || 0,
    hourly_rate: user?.hourly_rate || 0,
    availability: user?.availability || 'available'
  });

  const userRole = getUserRole();
  const skillOptions = [
    { value: 'plumbing', label: t('plumbing') },
    { value: 'electrical', label: t('electrical') },
    { value: 'carpentry', label: t('carpentry') },
    { value: 'painting', label: t('painting') },
    { value: 'gardening', label: t('gardening') },
    { value: 'cleaning', label: t('cleaning') },
    { value: 'appliance_repair', label: t('applianceRepair') },
    { value: 'other', label: t('other') }
  ];

  const availabilityOptions = [
    { value: 'available', label: t('available', 'Available'), color: 'text-green-600' },
    { value: 'busy', label: t('busy', 'Busy'), color: 'text-yellow-600' },
    { value: 'unavailable', label: t('unavailable', 'Unavailable'), color: 'text-red-600' }
  ];

  useEffect(() => {
    if (user) {
      setProfileData({
        name: user.name || '',
        email: user.email || '',
        phone: user.phone || '',
        location: user.location || '',
        bio: user.bio || '',
        skills: user.skills || [],
        experience_years: user.experience_years || 0,
        hourly_rate: user.hourly_rate || 0,
        availability: user.availability || 'available'
      });
    }
  }, [user]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSkillsChange = (skillValue) => {
    setProfileData(prev => ({
      ...prev,
      skills: prev.skills.includes(skillValue)
        ? prev.skills.filter(s => s !== skillValue)
        : [...prev.skills, skillValue]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await apiService.updateProfile(profileData);
      setSuccess(t('profileUpdatedSuccessfully', 'Profile updated successfully!'));
      
      // Update user context if needed
      if (response.data) {
        // The AuthContext should refresh the user data
      }
    } catch (err) {
      console.error('Profile update error:', err);
      setError(err.response?.data?.detail || t('profileUpdateError', 'Failed to update profile. Please try again.'));
    }

    setLoading(false);
  };

  const getRoleColor = () => {
    switch (userRole) {
      case 'admin': return 'border-red-500 bg-red-50';
      case 'fixer': return 'border-orange-500 bg-orange-50';
      case 'client': return 'border-blue-500 bg-blue-50';
      default: return 'border-gray-500 bg-gray-50';
    }
  };

  const getRoleIcon = () => {
    switch (userRole) {
      case 'admin': return '👨‍💼';
      case 'fixer': return '🔧';
      case 'client': return '👤';
      default: return '👤';
    }
  };

  const getRoleName = () => {
    switch (userRole) {
      case 'admin': return t('admin');
      case 'fixer': return t('fixer');
      case 'client': return t('client');
      default: return t('user', 'User');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-md">
        {/* Header */}
        <div className={`p-6 border-b-4 ${getRoleColor()}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-4xl">{getRoleIcon()}</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {t('myProfile')}
                </h1>
                <p className="text-gray-600">
                  {t('manageProfileInformation', 'Manage your profile information and preferences')}
                </p>
                <div className="mt-2">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleColor()}`}>
                    {getRoleName()}
                  </span>
                </div>
              </div>
            </div>
            <div>
              <LanguageSelector />
            </div>
          </div>
        </div>

        {/* Profile Form */}
        <div className="p-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
              <div className="text-sm text-red-600">{error}</div>
            </div>
          )}

          {success && (
            <div className="bg-green-50 border border-green-200 rounded-md p-4 mb-6">
              <div className="text-sm text-green-600">{success}</div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Basic Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                {t('basicInformation', 'Basic Information')}
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                    {t('fullName', 'Full Name')}
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={profileData.name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder={t('enterFullName', 'Enter your full name')}
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    {t('emailAddress', 'Email Address')}
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={profileData.email}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder={t('enterEmailAddress', 'Enter your email address')}
                  />
                </div>

                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                    {t('phoneNumber')}
                  </label>
                  <input
                    type="tel"
                    id="phone"
                    name="phone"
                    value={profileData.phone}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder={t('enterPhoneNumber')}
                  />
                </div>

                <div>
                  <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
                    {t('location')}
                  </label>
                  <input
                    type="text"
                    id="location"
                    name="location"
                    value={profileData.location}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder={t('enterLocation')}
                  />
                </div>
              </div>
            </div>

            {/* Bio */}
            <div>
              <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-2">
                {t('bio', 'Bio')}
              </label>
              <textarea
                id="bio"
                name="bio"
                value={profileData.bio}
                onChange={handleInputChange}
                rows="4"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder={t('tellUsAboutYourself', 'Tell us about yourself...')}
              />
            </div>

            {/* Fixer-specific fields */}
            {userRole === 'fixer' && (
              <>
                {/* Skills */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">
                    {t('professionalInformation', 'Professional Information')}
                  </h3>
                  
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {t('skills', 'Skills')}
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {skillOptions.map(skill => (
                        <label key={skill.value} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={profileData.skills.includes(skill.value)}
                            onChange={() => handleSkillsChange(skill.value)}
                            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                          />
                          <span className="ml-2 text-sm text-gray-700">{skill.label}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Experience & Rate */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div>
                      <label htmlFor="experience_years" className="block text-sm font-medium text-gray-700 mb-2">
                        {t('experienceYears', 'Years of Experience')}
                      </label>
                      <input
                        type="number"
                        id="experience_years"
                        name="experience_years"
                        value={profileData.experience_years}
                        onChange={handleInputChange}
                        min="0"
                        max="50"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      />
                    </div>

                    <div>
                      <label htmlFor="hourly_rate" className="block text-sm font-medium text-gray-700 mb-2">
                        {t('hourlyRate', 'Hourly Rate (R)')}
                      </label>
                      <input
                        type="number"
                        id="hourly_rate"
                        name="hourly_rate"
                        value={profileData.hourly_rate}
                        onChange={handleInputChange}
                        min="0"
                        step="10"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      />
                    </div>

                    <div>
                      <label htmlFor="availability" className="block text-sm font-medium text-gray-700 mb-2">
                        {t('availability', 'Availability')}
                      </label>
                      <select
                        id="availability"
                        name="availability"
                        value={profileData.availability}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                      >
                        {availabilityOptions.map(option => (
                          <option key={option.value} value={option.value}>
                            {option.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              </>
            )}

            {/* Submit Button */}
            <div className="flex items-center justify-between pt-6 border-t">
              <div className="text-sm text-gray-500">
                {t('lastUpdated', 'Last updated')}: {user?.updated_at ? new Date(user.updated_at).toLocaleDateString() : t('never', 'Never')}
              </div>
              
              <button
                type="submit"
                disabled={loading}
                className={`px-6 py-2 border border-transparent text-base font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed ${
                  userRole === 'admin' 
                    ? 'bg-red-600 hover:bg-red-700 focus:ring-red-500' 
                    : userRole === 'fixer'
                    ? 'bg-orange-600 hover:bg-orange-700 focus:ring-orange-500'
                    : 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
                }`}
              >
                {loading ? t('updating', 'Updating...') : t('updateProfile', 'Update Profile')}
              </button>
            </div>
          </form>
        </div>
      </div>

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
          {/* Debug: Test if component renders */}
          <div className="bg-yellow-100 border border-yellow-400 rounded p-4 mb-4">
            <h3 className="font-bold text-yellow-800">🔍 Debug: Push Notification Component Test</h3>
            <p className="text-yellow-700">If you can see this, the Profile component is rendering correctly.</p>
          </div>
          
          {/* Try-catch wrapper for PushNotificationManager */}
          <div className="push-notification-wrapper">
            <PushNotificationManager />
          </div>
          
          {/* Fallback content */}
          <div className="bg-blue-100 border border-blue-400 rounded p-4 mt-4">
            <h3 className="font-bold text-blue-800">🔔 Push Notifications</h3>
            <p className="text-blue-700">Push notification component should appear above this message.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;