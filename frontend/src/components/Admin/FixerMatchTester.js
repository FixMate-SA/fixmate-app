import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const FixerMatchTester = ({ fixerId, fixerName, onClose }) => {
  const { user } = useAuth();
  const [testJobData, setTestJobData] = useState({
    service: 'plumbing',
    description: '',
    location: '',
    latitude: '',
    longitude: '',
    estimated_price: '',
    priority_level: 'normal',
    client_language: 'english'
  });
  const [matchResult, setMatchResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const serviceOptions = [
    'plumbing', 'electrical', 'carpentry', 'painting', 'cleaning',
    'gardening', 'handyman', 'appliance repair', 'roofing', 'flooring',
    'hvac', 'tech support', 'tutoring', 'beauty services', 'catering', 'photography'
  ];

  const priorityOptions = [
    { value: 'normal', label: 'Normal' },
    { value: 'high', label: 'High Priority' },
    { value: 'urgent', label: 'Urgent' }
  ];

  const languageOptions = [
    { value: 'english', label: 'English' },
    { value: 'afrikaans', label: 'Afrikaans' },
    { value: 'zulu', label: 'isiZulu' },
    { value: 'xhosa', label: 'isiXhosa' },
    { value: 'sotho', label: 'Sesotho' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setTestJobData(prev => ({ ...prev, [name]: value }));
  };

  const handleTestMatch = async () => {
    if (!testJobData.description.trim()) {
      setError('Please provide a job description');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/fixer/${fixerId}/match-test`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            ...testJobData,
            estimated_price: testJobData.estimated_price ? parseFloat(testJobData.estimated_price) : 300.0,
            latitude: testJobData.latitude ? parseFloat(testJobData.latitude) : null,
            longitude: testJobData.longitude ? parseFloat(testJobData.longitude) : null
          })
        }
      );

      if (response.ok) {
        const data = await response.json();
        setMatchResult(data.match_result);
      } else {
        setError('Failed to test match');
      }
    } catch (err) {
      console.error('Error testing match:', err);
      setError('Error testing match');
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score, maxScore) => {
    const percentage = (score / maxScore) * 100;
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-blue-600';
    if (percentage >= 40) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getRecommendationBadge = (recommendation) => {
    const colors = {
      excellent: 'bg-green-100 text-green-800',
      good: 'bg-blue-100 text-blue-800',
      fair: 'bg-yellow-100 text-yellow-800',
      poor: 'bg-red-100 text-red-800'
    };
    
    const icons = {
      excellent: '⭐',
      good: '👍',
      fair: '👌',
      poor: '⚠️'
    };

    return (
      <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium ${colors[recommendation]}`}>
        <span>{icons[recommendation]}</span>
        <span className="capitalize">{recommendation} Match</span>
      </span>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">🧪 Fixer Match Test</h2>
              <p className="text-gray-600">Testing match quality for: <span className="font-medium">{fixerName}</span></p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Test Job Form */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Create Test Job</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Service Type
                </label>
                <select
                  name="service"
                  value={testJobData.service}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {serviceOptions.map(service => (
                    <option key={service} value={service}>
                      {service.charAt(0).toUpperCase() + service.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description *
                </label>
                <textarea
                  name="description"
                  value={testJobData.description}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="Describe the test job in detail..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <input
                  type="text"
                  name="location"
                  value={testJobData.location}
                  onChange={handleInputChange}
                  placeholder="e.g., Cape Town CBD"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Latitude (Optional)
                  </label>
                  <input
                    type="number"
                    name="latitude"
                    value={testJobData.latitude}
                    onChange={handleInputChange}
                    step="0.000001"
                    placeholder="-33.9249"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Longitude (Optional)
                  </label>
                  <input
                    type="number"
                    name="longitude"
                    value={testJobData.longitude}
                    onChange={handleInputChange}
                    step="0.000001"
                    placeholder="18.4241"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Estimated Budget (R)
                </label>
                <input
                  type="number"
                  name="estimated_price"
                  value={testJobData.estimated_price}
                  onChange={handleInputChange}
                  min="0"
                  step="0.01"
                  placeholder="300.00"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Priority Level
                  </label>
                  <select
                    name="priority_level"
                    value={testJobData.priority_level}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {priorityOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Client Language
                  </label>
                  <select
                    name="client_language"
                    value={testJobData.client_language}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {languageOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
                  {error}
                </div>
              )}

              <button
                onClick={handleTestMatch}
                disabled={loading}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {loading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Testing Match...</span>
                  </div>
                ) : (
                  'Test Match Quality'
                )}
              </button>
            </div>

            {/* Match Results */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900">Match Results</h3>
              
              {matchResult ? (
                <div className="space-y-4">
                  {/* Overall Score */}
                  <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium text-gray-900">Overall Match Score</h4>
                      {getRecommendationBadge(matchResult.recommendation)}
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className={`text-3xl font-bold ${getScoreColor(matchResult.total_score, matchResult.max_possible_score)}`}>
                        {matchResult.total_score}
                      </div>
                      <div className="text-gray-500">
                        / {matchResult.max_possible_score} points ({matchResult.percentage}%)
                      </div>
                    </div>
                    {matchResult.explanation && (
                      <p className="text-sm text-gray-600 mt-2">{matchResult.explanation}</p>
                    )}
                  </div>

                  {/* Factor Breakdown */}
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-3">Score Breakdown</h4>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Skill Match:</span>
                        <span className="font-medium text-blue-600">{Math.round(matchResult.factors.skill_match)}/30</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Success Rate:</span>
                        <span className="font-medium text-green-600">{Math.round(matchResult.factors.success_rate)}/20</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Location:</span>
                        <span className="font-medium text-purple-600">{Math.round(matchResult.factors.location_score)}/20</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Availability:</span>
                        <span className="font-medium text-orange-600">{Math.round(matchResult.factors.availability)}/15</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Language Match:</span>
                        <span className="font-medium text-indigo-600">{Math.round(matchResult.factors.preference_match)}/10</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Reliability:</span>
                        <span className="font-medium text-red-600">{Math.round(matchResult.factors.reliability)}/15</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Fair Distribution:</span>
                        <span className="font-medium text-cyan-600">{Math.round(matchResult.factors.fairness_boost)}/10</span>
                      </div>
                    </div>
                  </div>

                  {/* Visual Score Bar */}
                  <div className="bg-white border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-3">Visual Score Representation</h4>
                    <div className="w-full bg-gray-200 rounded-full h-4 mb-2">
                      <div
                        className={`h-4 rounded-full transition-all duration-500 ${
                          matchResult.percentage >= 80 ? 'bg-green-500' :
                          matchResult.percentage >= 60 ? 'bg-blue-500' :
                          matchResult.percentage >= 40 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${Math.min(matchResult.percentage, 100)}%` }}
                      ></div>
                    </div>
                    <div className="text-xs text-gray-500 text-center">
                      {matchResult.percentage}% match quality
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <div className="text-4xl mb-2">🎯</div>
                  <p>Fill out the test job details and click "Test Match Quality" to see how well this fixer matches the job requirements.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FixerMatchTester;