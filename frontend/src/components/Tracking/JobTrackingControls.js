import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import api from '../../services/api';

const JobTrackingControls = ({ jobId, onTrackingUpdate }) => {
  const { user } = useAuth();
  const { language, translations } = useLanguage();
  const [trackingState, setTrackingState] = useState('idle'); // idle, tracking, completed
  const [trackingId, setTrackingId] = useState(null);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [estimatedArrival, setEstimatedArrival] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [locationWatch, setLocationWatch] = useState(null);

  // Get current location
  const getCurrentLocation = () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by this browser'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
            accuracy: position.coords.accuracy
          });
        },
        (error) => reject(error),
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    });
  };

  // Start job tracking
  const startTracking = async () => {
    try {
      setLoading(true);
      setError('');

      // Get current location as departure location
      const location = await getCurrentLocation();
      
      const response = await api.post(`/jobs/${jobId}/tracking/start`, {
        departure_location: location
      });

      if (response.data.success) {
        setTrackingState('tracking');
        setTrackingId(response.data.tracking_id);
        setEstimatedArrival(response.data.estimated_arrival);
        setCurrentLocation(location);
        
        // Start watching location
        startLocationWatch();
        
        if (onTrackingUpdate) {
          onTrackingUpdate({
            status: 'tracking',
            trackingId: response.data.tracking_id,
            estimatedArrival: response.data.estimated_arrival
          });
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start tracking');
    } finally {
      setLoading(false);
    }
  };

  // Start location watching
  const startLocationWatch = () => {
    if (navigator.geolocation) {
      const watchId = navigator.geolocation.watchPosition(
        async (position) => {
          const location = {
            lat: position.coords.latitude,
            lng: position.coords.longitude
          };
          
          setCurrentLocation(location);
          await updateLocation(location, position.coords.accuracy);
        },
        (error) => console.error('Location watch error:', error),
        { 
          enableHighAccuracy: true, 
          timeout: 30000, 
          maximumAge: 10000 
        }
      );
      
      setLocationWatch(watchId);
    }
  };

  // Update location
  const updateLocation = async (location, accuracy) => {
    try {
      const response = await api.post(`/jobs/${jobId}/tracking/location`, {
        location,
        accuracy
      });

      if (response.data.success) {
        setEstimatedArrival(response.data.estimated_arrival);
        
        if (onTrackingUpdate) {
          onTrackingUpdate({
            status: 'tracking',
            location,
            estimatedArrival: response.data.estimated_arrival,
            distanceToJob: response.data.distance_to_job
          });
        }
      }
    } catch (err) {
      console.error('Failed to update location:', err);
    }
  };

  // Complete tracking
  const completeTracking = async () => {
    try {
      setLoading(true);
      setError('');

      const response = await api.post(`/jobs/${jobId}/tracking/complete`);

      if (response.data.success) {
        setTrackingState('completed');
        
        // Stop location watching
        if (locationWatch) {
          navigator.geolocation.clearWatch(locationWatch);
          setLocationWatch(null);
        }
        
        if (onTrackingUpdate) {
          onTrackingUpdate({
            status: 'completed',
            completedAt: new Date().toISOString()
          });
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to complete tracking');
    } finally {
      setLoading(false);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (locationWatch) {
        navigator.geolocation.clearWatch(locationWatch);
      }
    };
  }, [locationWatch]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-semibold text-gray-800 mb-4">
        {translations.job_tracking || 'Job Tracking'}
      </h3>

      {error && (
        <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {/* Tracking Status */}
        <div className="flex items-center space-x-3">
          <div className={`w-3 h-3 rounded-full ${
            trackingState === 'idle' ? 'bg-gray-400' :
            trackingState === 'tracking' ? 'bg-green-500 animate-pulse' :
            'bg-blue-500'
          }`}></div>
          <span className="text-sm font-medium text-gray-700">
            {trackingState === 'idle' && (translations.tracking_not_started || 'Tracking Not Started')}
            {trackingState === 'tracking' && (translations.tracking_active || 'Tracking Active')}
            {trackingState === 'completed' && (translations.tracking_completed || 'Tracking Completed')}
          </span>
        </div>

        {/* Current Location */}
        {currentLocation && (
          <div className="bg-gray-50 p-3 rounded">
            <p className="text-sm text-gray-600 mb-1">
              {translations.current_location || 'Current Location:'}
            </p>
            <p className="text-xs text-gray-500">
              Lat: {currentLocation.lat.toFixed(6)}, Lng: {currentLocation.lng.toFixed(6)}
            </p>
          </div>
        )}

        {/* Estimated Arrival */}
        {estimatedArrival && (
          <div className="bg-blue-50 p-3 rounded">
            <p className="text-sm text-blue-800 font-medium">
              {translations.estimated_arrival || 'Estimated Arrival:'} {new Date(estimatedArrival).toLocaleTimeString()}
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-3">
          {trackingState === 'idle' && (
            <button
              onClick={startTracking}
              disabled={loading}
              className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  {translations.starting || 'Starting...'}
                </div>
              ) : (
                translations.start_tracking || 'Start Tracking'
              )}
            </button>
          )}

          {trackingState === 'tracking' && (
            <button
              onClick={completeTracking}
              disabled={loading}
              className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  {translations.completing || 'Completing...'}
                </div>
              ) : (
                translations.complete_tracking || 'Complete Tracking'
              )}
            </button>
          )}
        </div>

        {/* Instructions */}
        <div className="text-xs text-gray-500 bg-gray-50 p-3 rounded">
          {trackingState === 'idle' && (
            <p>{translations.tracking_start_instruction || 'Click "Start Tracking" when you begin traveling to the job location. This will share your live location with the client.'}</p>
          )}
          {trackingState === 'tracking' && (
            <p>{translations.tracking_active_instruction || 'Your location is being shared with the client. Click "Complete Tracking" when you arrive at the job location.'}</p>
          )}
          {trackingState === 'completed' && (
            <p>{translations.tracking_completed_instruction || 'Tracking completed. The client has been notified of your arrival.'}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobTrackingControls;