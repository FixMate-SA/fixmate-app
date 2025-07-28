import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';

const EmergencyButton = ({ jobId = null, className = '' }) => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [isEmergency, setIsEmergency] = useState(false);
  const [loading, setLoading] = useState(false);
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState(null);
  const [alertSent, setAlertSent] = useState(false);

  const getCurrentLocation = () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          });
        },
        (error) => {
          reject(error);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000
        }
      );
    });
  };

  const getLocationAddress = async (lat, lng) => {
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/emergency/location?latitude=${lat}&longitude=${lng}`
      );
      const data = await response.json();
      return data.address;
    } catch (error) {
      return `${lat}, ${lng}`;
    }
  };

  const handleEmergencyClick = () => {
    setIsEmergency(true);
  };

  const sendEmergencyAlert = async () => {
    if (!user) return;

    setLoading(true);

    try {
      // Get current location
      const position = await getCurrentLocation();
      const address = await getLocationAddress(position.latitude, position.longitude);
      
      setLocation({ ...position, address });

      // Send emergency alert
      const formData = new FormData();
      formData.append('user_id', user.id);
      formData.append('job_id', jobId || '');
      formData.append('alert_type', 'emergency');
      formData.append('latitude', position.latitude.toString());
      formData.append('longitude', position.longitude.toString());
      formData.append('address', address);
      formData.append('description', description || 'Emergency assistance requested');

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/emergency/alert`, {
        method: 'POST',
        body: formData
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setAlertSent(true);
      } else {
        throw new Error(result.detail || 'Failed to send emergency alert');
      }
    } catch (error) {
      console.error('Emergency alert failed:', error);
      alert('Failed to send emergency alert. Please call 10111 directly for immediate assistance.');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setIsEmergency(false);
    setDescription('');
    setAlertSent(false);
  };

  if (alertSent) {
    return (
      <div className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 ${className}`}>
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div className="text-center">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {t('emergencyAlertSent', 'Emergency Alert Sent!')}
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              {t('policeNotified', 'Police have been notified and your location has been shared. Help is on the way.')}
            </p>
            {location && (
              <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded-md mb-4">
                <p><strong>Location:</strong> {location.address}</p>
                <p><strong>Coordinates:</strong> {location.latitude.toFixed(6)}, {location.longitude.toFixed(6)}</p>
              </div>
            )}
            <button
              onClick={handleCancel}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              {t('close', 'Close')}
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (isEmergency) {
    return (
      <div className={`fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 ${className}`}>
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div className="text-center mb-4">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L4.316 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {t('emergencyAlert', 'Emergency Alert')}
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              {t('emergencyDescription', 'This will immediately notify police and share your current location. Only use in real emergencies.')}
            </p>
          </div>

          <div className="mb-4">
            <label htmlFor="emergency-description" className="block text-sm font-medium text-gray-700 mb-2">
              {t('whatIsHappening', 'What is happening?')} ({t('optional', 'Optional')})
            </label>
            <textarea
              id="emergency-description"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder={t('emergencyPlaceholder', 'Briefly describe the emergency situation...')}
            />
          </div>

          <div className="flex space-x-3">
            <button
              onClick={handleCancel}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
              disabled={loading}
            >
              {t('cancel', 'Cancel')}
            </button>
            <button
              onClick={sendEmergencyAlert}
              disabled={loading}
              className="flex-1 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center justify-center"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>{t('alerting', 'Alerting...')}</span>
                </div>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18.5c3.5-2 5.5-4.5 5.5-7.5 0-4.5-3-8-8-8s-8 3.5-8 8c0 3 2 5.5 5.5 7.5" />
                  </svg>
                  {t('sendAlert', 'Send Emergency Alert')}
                </>
              )}
            </button>
          </div>

          <div className="mt-4 text-xs text-gray-500 text-center">
            <p>🚨 {t('emergencyWarning', 'For immediate danger, call 10111 directly')}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <button
      onClick={handleEmergencyClick}
      className={`bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 font-medium transition-colors ${className}`}
      title={t('emergencyButtonTitle', 'Emergency - Get immediate help')}
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.728-.833-2.498 0L4.316 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
      <span>{t('emergency', 'Emergency')}</span>
    </button>
  );
};

export default EmergencyButton;