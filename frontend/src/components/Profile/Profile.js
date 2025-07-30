import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/api';
import FixerPaymentManager from '../Payment/FixerPaymentManager';
import LanguageSelector from '../Common/LanguageSelector';
import Logo from '../Common/Logo';

const Profile = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [fixer, setFixer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    address: ''
  });

  useEffect(() => {
    // Check if user is also a fixer
    const fetchFixerData = async () => {
      try {
        if (user?.phone) {
          const fixers = await apiService.getFixers();
          const userFixer = fixers.data?.find(f => f.phone === user.phone);
          setFixer(userFixer);
        }
      } catch (error) {
        console.error('Error fetching fixer data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFixerData();
  }, [user]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Profile Header */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-2xl font-bold">
                {user?.name?.charAt(0)?.toUpperCase()}
              </span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{user?.name}</h1>
              <p className="text-gray-600">{user?.phone}</p>
              {fixer && (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  {t('fixer', 'Fixer')} • Rating: {fixer.rating.toFixed(1)}⭐
                </span>
              )}
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <LanguageSelector />
            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              {t('editProfile', 'Edit Profile')}
            </button>
          </div>
        </div>
      </div>

      {/* Profile Tabs */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('profile')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'profile'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('profile', 'Profile')}
            </button>

            {fixer && (
              <>
                <button
                  onClick={() => setActiveTab('payments')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'payments'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {t('payments', 'Payments')}
                </button>

                <button
                  onClick={() => setActiveTab('verification')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === 'verification'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {t('verification', 'Verification')}
                </button>
              </>
            )}

            <button
              onClick={() => setActiveTab('settings')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'settings'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {t('settings', 'Settings')}
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-lg font-medium mb-4">
                    {t('personalInfo', 'Personal Information')}
                  </h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        {t('name', 'Name')}
                      </label>
                      <div className="mt-1 p-3 bg-gray-50 border border-gray-200 rounded-md">
                        {user?.name}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        {t('phoneNumber', 'Phone Number')}
                      </label>
                      <div className="mt-1 p-3 bg-gray-50 border border-gray-200 rounded-md">
                        {user?.phone}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700">
                        {t('email', 'Email')}
                      </label>
                      <div className="mt-1 p-3 bg-gray-50 border border-gray-200 rounded-md">
                        {user?.email || t('notProvided', 'Not provided')}
                      </div>
                    </div>
                  </div>
                </div>

                {fixer && (
                  <div>
                    <h3 className="text-lg font-medium mb-4">
                      {t('fixerInfo', 'Fixer Information')}
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          {t('services', 'Services')}
                        </label>
                        <div className="mt-1">
                          {JSON.parse(fixer.services).map((service, index) => (
                            <span
                              key={index}
                              className="inline-block bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded mr-2 mb-2"
                            >
                              {service}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          {t('location', 'Location')}
                        </label>
                        <div className="mt-1 p-3 bg-gray-50 border border-gray-200 rounded-md">
                          {fixer.location}
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700">
                          {t('statistics', 'Statistics')}
                        </label>
                        <div className="mt-1 grid grid-cols-3 gap-4">
                          <div className="bg-green-50 p-3 rounded-md text-center">
                            <div className="text-2xl font-bold text-green-600">
                              {fixer.rating.toFixed(1)}
                            </div>
                            <div className="text-sm text-gray-600">
                              {t('rating', 'Rating')}
                            </div>
                          </div>
                          <div className="bg-blue-50 p-3 rounded-md text-center">
                            <div className="text-2xl font-bold text-blue-600">
                              {fixer.total_jobs}
                            </div>
                            <div className="text-sm text-gray-600">
                              {t('totalJobs', 'Total Jobs')}
                            </div>
                          </div>
                          <div className="bg-purple-50 p-3 rounded-md text-center">
                            <div className={`text-2xl font-bold ${
                              fixer.is_active ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {fixer.is_active ? '✓' : '✗'}
                            </div>
                            <div className="text-sm text-gray-600">
                              {t('status', 'Status')}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'payments' && fixer && (
            <div>
              <h3 className="text-lg font-medium mb-4">
                {t('paymentManagement', 'Payment Management')}
              </h3>
              <FixerPaymentManager fixerId={fixer.id} />
            </div>
          )}

          {activeTab === 'verification' && fixer && (
            <div>
              <h3 className="text-lg font-medium mb-4">
                {t('documentVerification', 'Document Verification')}
              </h3>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">
                      {t('verificationRequired', 'Verification Required')}
                    </h3>
                    <div className="mt-2 text-sm text-yellow-700">
                      <p>
                        {t('verificationMessage', 'Please upload your ID document for verification. This helps build trust with customers.')}
                      </p>
                    </div>
                    <div className="mt-4">
                      <button className="bg-yellow-100 hover:bg-yellow-200 text-yellow-800 font-medium py-2 px-4 rounded">
                        {t('uploadID', 'Upload ID Document')}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-4">
                  {t('languagePreferences', 'Language Preferences')}
                </h3>
                <div className="flex items-center space-x-4">
                  <label className="text-sm font-medium text-gray-700">
                    {t('selectLanguage', 'Select Language')}:
                  </label>
                  <LanguageSelector />
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium mb-4">
                  {t('notifications', 'Notification Preferences')}
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center">
                    <input
                      id="sms-notifications"
                      name="sms-notifications"
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      defaultChecked
                    />
                    <label htmlFor="sms-notifications" className="ml-2 block text-sm text-gray-900">
                      {t('smsNotifications', 'SMS Notifications')}
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      id="job-alerts"
                      name="job-alerts"
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      defaultChecked
                    />
                    <label htmlFor="job-alerts" className="ml-2 block text-sm text-gray-900">
                      {t('jobAlerts', 'Job Alerts')}
                    </label>
                  </div>
                  <div className="flex items-center">
                    <input
                      id="payment-reminders"
                      name="payment-reminders"
                      type="checkbox"
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      defaultChecked
                    />
                    <label htmlFor="payment-reminders" className="ml-2 block text-sm text-gray-900">
                      {t('paymentReminders', 'Payment Reminders')}
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;