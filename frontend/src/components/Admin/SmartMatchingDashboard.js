import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const SmartMatchingDashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [performanceData, setPerformanceData] = useState(null);
  const [improvements, setImprovements] = useState(null);
  const [error, setError] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState(7);
  const [loadingImprovements, setLoadingImprovements] = useState(false);

  useEffect(() => {
    if (user?.role === 'admin' || user?.role === 'super_admin') {
      fetchPerformanceData();
    }
  }, [user, selectedPeriod]);

  const fetchPerformanceData = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/matching-performance?days=${selectedPeriod}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPerformanceData(data.performance_analysis);
      } else {
        setError('Failed to load performance data');
      }
    } catch (err) {
      console.error('Error fetching performance data:', err);
      setError('Error loading performance data');
    } finally {
      setLoading(false);
    }
  };

  const fetchImprovements = async () => {
    setLoadingImprovements(true);
    
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/improve-matching`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            analysis_days: selectedPeriod
          })
        }
      );

      if (response.ok) {
        const data = await response.json();
        setImprovements(data);
      } else {
        setError('Failed to load improvement suggestions');
      }
    } catch (err) {
      console.error('Error fetching improvements:', err);
      setError('Error loading improvement suggestions');
    } finally {
      setLoadingImprovements(false);
    }
  };

  const getPerformanceColor = (rating) => {
    switch (rating) {
      case 'excellent': return 'text-green-600 bg-green-50 border-green-200';
      case 'good': return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'fair': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-red-600 bg-red-50 border-red-200';
    }
  };

  const getPerformanceIcon = (rating) => {
    switch (rating) {
      case 'excellent': return '🏆';
      case 'good': return '👍';
      case 'fair': return '👌';
      default: return '⚠️';
    }
  };

  if (user?.role !== 'admin' && user?.role !== 'super_admin') {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          Access denied. Admin privileges required.
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">🎯 Smart Matching Analytics</h1>
        <p className="text-gray-600">AI-powered job matching performance and optimization insights</p>
      </div>

      {/* Period Selection */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Analysis Period</h2>
          <div className="flex space-x-2">
            {[7, 14, 30].map((days) => (
              <button
                key={days}
                onClick={() => setSelectedPeriod(days)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  selectedPeriod === days
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {days} days
              </button>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading performance analytics...</p>
          </div>
        </div>
      ) : performanceData ? (
        <>
          {/* Performance Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Jobs</p>
                  <p className="text-2xl font-bold text-gray-900">{performanceData.total_jobs}</p>
                </div>
                <div className="text-3xl">📊</div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Assignment Rate</p>
                  <p className="text-2xl font-bold text-blue-600">{performanceData.assignment_rate}%</p>
                </div>
                <div className="text-3xl">🎯</div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Completion Rate</p>
                  <p className="text-2xl font-bold text-green-600">{performanceData.completion_rate}%</p>
                </div>
                <div className="text-3xl">✅</div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Avg Assignment Time</p>
                  <p className="text-2xl font-bold text-purple-600">{performanceData.avg_assignment_time_minutes}m</p>
                </div>
                <div className="text-3xl">⏱️</div>
              </div>
            </div>
          </div>

          {/* Performance Rating */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Performance Rating</h3>
            <div className={`inline-flex items-center space-x-3 px-4 py-3 rounded-lg border ${getPerformanceColor(performanceData.performance_rating)}`}>
              <span className="text-2xl">{getPerformanceIcon(performanceData.performance_rating)}</span>
              <div>
                <div className="font-semibold capitalize">{performanceData.performance_rating}</div>
                <div className="text-sm opacity-75">System Performance Level</div>
              </div>
            </div>
          </div>

          {/* AI Improvements Section */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">🤖 AI-Powered Improvement Suggestions</h3>
              <button
                onClick={fetchImprovements}
                disabled={loadingImprovements}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {loadingImprovements ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Analyzing...</span>
                  </div>
                ) : (
                  'Generate AI Recommendations'
                )}
              </button>
            </div>

            {improvements ? (
              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h4 className="font-medium text-blue-900 mb-2">Analysis Summary</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div className="text-center">
                      <div className="font-semibold text-blue-800">{improvements.analysis_period_days}</div>
                      <div className="text-blue-600">Days Analyzed</div>
                    </div>
                    <div className="text-center">
                      <div className="font-semibold text-blue-800">{improvements.problematic_jobs_count}</div>
                      <div className="text-blue-600">Unassigned Jobs</div>
                    </div>
                  </div>
                </div>

                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-3">🔍 AI Analysis & Recommendations</h4>
                  <div className="bg-white border border-gray-200 rounded p-3">
                    <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                      {improvements.ai_recommendations}
                    </pre>
                  </div>
                </div>

                <div className="text-xs text-gray-500 border-t pt-3">
                  Analysis generated by: {improvements.analyzed_by} on {new Date(improvements.generated_at).toLocaleString()}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <div className="text-4xl mb-2">🤖</div>
                <p>Click "Generate AI Recommendations" to get personalized improvement suggestions based on your matching performance data.</p>
              </div>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
};

export default SmartMatchingDashboard;