import React, { useState, useEffect } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import api from '../../services/api';

const JobTrackingStatus = ({ jobId, refreshInterval = 30000 }) => {
  const { language, translations } = useLanguage();
  const [trackingData, setTrackingData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [lastUpdated, setLastUpdated] = useState(null);

  // Fetch tracking status
  const fetchTrackingStatus = async () => {
    try {
      const response = await api.get(`/jobs/${jobId}/tracking/status`);
      
      if (response.data.success) {
        setTrackingData(response.data.tracking);
        setLastUpdated(new Date());
        setError('');
      } else {
        setTrackingData(null);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch tracking status');
    } finally {
      setLoading(false);
    }
  };

  // Calculate time until arrival
  const getTimeUntilArrival = (estimatedArrival) => {
    if (!estimatedArrival) return null;
    
    const now = new Date();
    const arrival = new Date(estimatedArrival);
    const diffMs = arrival.getTime() - now.getTime();
    
    if (diffMs <= 0) return 'Arrived';
    
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    
    if (diffHours > 0) {
      return `${diffHours}h ${diffMins % 60}m`;
    }
    return `${diffMins}m`;
  };

  // Format distance
  const formatDistance = (distance) => {
    if (!distance) return null;
    
    if (distance < 1000) {
      return `${Math.round(distance)}m`;
    }
    return `${(distance / 1000).toFixed(1)}km`;
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'started':
      case 'en_route':
        return 'text-blue-600 bg-blue-100';
      case 'near_location':
        return 'text-orange-600 bg-orange-100';
      case 'arrived':
      case 'completed':
        return 'text-green-600 bg-green-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  // Get status text
  const getStatusText = (status) => {
    const statusMap = {
      'started': translations.fixer_departed || 'Fixer has departed',
      'en_route': translations.fixer_en_route || 'Fixer is on the way',
      'near_location': translations.fixer_nearby || 'Fixer is nearby',
      'arrived': translations.fixer_arrived || 'Fixer has arrived',
      'completed': translations.tracking_finished || 'Tracking completed'
    };
    
    return statusMap[status] || status;
  };

  useEffect(() => {
    fetchTrackingStatus();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchTrackingStatus, refreshInterval);
    
    return () => clearInterval(interval);
  }, [jobId, refreshInterval]);

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">
          {translations.fixer_location || 'Fixer Location'}
        </h3>
        <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      </div>
    );
  }

  if (!trackingData) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">
          {translations.fixer_location || 'Fixer Location'}
        </h3>
        <div className="text-center py-8">
          <div className="text-gray-400 mb-2">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <p className="text-gray-500">
            {translations.no_tracking_available || 'Live tracking not available for this job'}
          </p>
        </div>
      </div>
    );
  }

  const timeUntilArrival = getTimeUntilArrival(trackingData.estimated_arrival);
  const distance = formatDistance(trackingData.distance_to_job);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-gray-800">
          {translations.fixer_location || 'Fixer Location'}
        </h3>
        <div className="text-xs text-gray-500">
          {translations.last_updated || 'Updated'}: {lastUpdated?.toLocaleTimeString()}
        </div>
      </div>

      <div className="space-y-4">
        {/* Status Badge */}
        <div className="flex items-center">
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(trackingData.status)}`}>
            <div className="w-2 h-2 bg-current rounded-full mr-2 animate-pulse"></div>
            {getStatusText(trackingData.status)}
          </div>
        </div>

        {/* ETA and Distance */}
        <div className="grid grid-cols-2 gap-4">
          {timeUntilArrival && (
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-xs text-blue-600 font-medium uppercase tracking-wide">
                {translations.estimated_arrival || 'ETA'}
              </div>
              <div className="text-2xl font-bold text-blue-800 mt-1">
                {timeUntilArrival === 'Arrived' ? (
                  <span className="text-green-600">{translations.arrived || 'Arrived'}</span>
                ) : (
                  timeUntilArrival
                )}
              </div>
            </div>
          )}

          {distance && (
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-xs text-gray-600 font-medium uppercase tracking-wide">
                {translations.distance || 'Distance'}
              </div>
              <div className="text-2xl font-bold text-gray-800 mt-1">
                {distance}
              </div>
            </div>
          )}
        </div>

        {/* Current Location */}
        {trackingData.current_location && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="text-sm font-medium text-gray-700 mb-2">
              {translations.current_location || 'Current Location'}
            </h4>
            <div className="text-xs text-gray-500">
              Lat: {trackingData.current_location.lat?.toFixed(6)}, 
              Lng: {trackingData.current_location.lng?.toFixed(6)}
            </div>
            {trackingData.current_location.accuracy && (
              <div className="text-xs text-gray-400 mt-1">
                {translations.accuracy || 'Accuracy'}: ±{Math.round(trackingData.current_location.accuracy)}m
              </div>
            )}
          </div>
        )}

        {/* Progress Bar */}
        {trackingData.progress_percentage !== undefined && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex justify-between text-sm text-gray-600 mb-2">
              <span>{translations.progress || 'Progress'}</span>
              <span>{Math.round(trackingData.progress_percentage)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${trackingData.progress_percentage}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Live Tracking Indicator */}
        <div className="flex items-center justify-center text-xs text-gray-500 border-t pt-4">
          <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
          {translations.live_tracking || 'Live tracking active'}
        </div>
      </div>
    </div>
  );
};

export default JobTrackingStatus;