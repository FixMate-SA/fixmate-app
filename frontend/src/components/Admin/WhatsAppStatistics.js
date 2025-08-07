import React, { useState, useEffect } from 'react';
import apiService from '../../services/api';

const WhatsAppStatistics = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeFilter, setTimeFilter] = useState(24);

  useEffect(() => {
    fetchStatistics();
  }, [timeFilter]);

  const fetchStatistics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.getWhatsAppStatistics(timeFilter);
      setStats(response);
      
    } catch (error) {
      console.error('Error fetching WhatsApp statistics:', error);
      setError('Failed to load statistics');
      
      // Fallback to show zeros instead of placeholders
      setStats({
        messages_sent: 0,
        messages_received: 0,
        service_requests: 0,
        active_conversations: 0,
        urgent_requests: 0,
        webapp_redirects: 0,
        time_period: `${timeFilter}h`
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    fetchStatistics();
  };

  const formatNumber = (num) => {
    if (num === null || num === undefined) return '--';
    return num.toLocaleString();
  };

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h4 className="font-medium text-gray-900">
            WhatsApp Message Statistics ({stats?.time_period || `${timeFilter}h`})
          </h4>
          <div className="flex items-center gap-3">
            {/* Time Filter */}
            <select
              value={timeFilter}
              onChange={(e) => setTimeFilter(parseInt(e.target.value))}
              className="text-sm border border-gray-300 rounded px-2 py-1 bg-white"
            >
              <option value={24}>Last 24 Hours</option>
              <option value={72}>Last 3 Days</option>
              <option value={168}>Last Week</option>
              <option value={720}>Last 30 Days</option>
            </select>
            
            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="text-sm bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1"
            >
              <svg className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>
        
        {error && (
          <div className="mt-2 text-sm text-red-600 flex items-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            {error} - Showing zeros as fallback
          </div>
        )}
      </div>
      
      <div className="p-6">
        {loading && !stats ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
            <span className="ml-2 text-gray-600">Loading statistics...</span>
          </div>
        ) : (
          <>
            {/* Main Statistics Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center mb-6">
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {formatNumber(stats?.messages_sent)}
                </div>
                <div className="text-sm text-gray-600 mt-1">Messages Sent</div>
                <div className="text-xs text-blue-500 mt-1">To Customers</div>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {formatNumber(stats?.messages_received)}
                </div>
                <div className="text-sm text-gray-600 mt-1">Messages Received</div>
                <div className="text-xs text-green-500 mt-1">From Customers</div>
              </div>
              
              <div className="bg-orange-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {formatNumber(stats?.service_requests)}
                </div>
                <div className="text-sm text-gray-600 mt-1">Service Requests</div>
                <div className="text-xs text-orange-500 mt-1">Detected Services</div>
              </div>
              
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {formatNumber(stats?.active_conversations)}
                </div>
                <div className="text-sm text-gray-600 mt-1">Active Conversations</div>
                <div className="text-xs text-purple-500 mt-1">Unique Customers</div>
              </div>
            </div>

            {/* Additional Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="bg-red-50 p-4 rounded-lg text-center">
                <div className="text-xl font-bold text-red-600">
                  {formatNumber(stats?.urgent_requests)}
                </div>
                <div className="text-sm text-gray-600 mt-1">Urgent Requests</div>
                <div className="text-xs text-red-500 mt-1">High Priority</div>
              </div>
              
              <div className="bg-indigo-50 p-4 rounded-lg text-center">
                <div className="text-xl font-bold text-indigo-600">
                  {formatNumber(stats?.webapp_redirects)}
                </div>
                <div className="text-sm text-gray-600 mt-1">Web App Redirects</div>
                <div className="text-xs text-indigo-500 mt-1">Successful Guidance</div>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-lg text-center">
                <div className="text-xl font-bold text-gray-600">
                  {stats?.messages_received > 0 
                    ? Math.round((stats?.webapp_redirects || 0) / stats?.messages_received * 100)
                    : 0
                  }%
                </div>
                <div className="text-sm text-gray-600 mt-1">Conversion Rate</div>
                <div className="text-xs text-gray-500 mt-1">To Web App</div>
              </div>
            </div>

            {/* Top Services (if available) */}
            {stats?.top_services && stats.top_services.length > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h5 className="font-medium text-gray-900 mb-3">Top Requested Services</h5>
                <div className="space-y-2">
                  {stats.top_services.map((service, index) => (
                    <div key={service.service || index} className="flex items-center justify-between">
                      <span className="text-sm capitalize text-gray-700">
                        🔧 {service.service || 'Unknown'}
                      </span>
                      <span className="text-sm font-medium text-gray-900">
                        {service.count} requests
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Last Updated */}
            <div className="mt-4 text-xs text-gray-500 text-center">
              Last updated: {stats?.last_updated 
                ? new Date(stats.last_updated).toLocaleString()
                : 'Never'
              }
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default WhatsAppStatistics;