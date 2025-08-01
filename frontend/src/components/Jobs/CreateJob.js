import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import { useNavigate } from 'react-router-dom';
import VoiceRecorder from '../VoiceRecorder/VoiceRecorder';
import TermsAcceptance from '../Workflow/TermsAcceptance';

const CreateJob = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    service: '',
    description: '',
    location: '',
    estimated_price: '',
    scheduled_at: '',
  });
  
  const [loading, setLoading] = useState(false);
  const [smartMatchLoading, setSmartMatchLoading] = useState(false);
  const [error, setError] = useState('');
  const [showVoiceRecorder, setShowVoiceRecorder] = useState(false);
  const [smartMatches, setSmartMatches] = useState([]);
  const [matchInsights, setMatchInsights] = useState(null);
  const [showSmartMatching, setShowSmartMatching] = useState(false);
  const [createdJobId, setCreatedJobId] = useState(null);
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [jobBeingCancelled, setJobBeingCancelled] = useState(null);

  const serviceOptions = [
    'Plumbing',
    'Electrical',
    'Carpentry',
    'Painting',
    'Cleaning',
    'Gardening',
    'Handyman',
    'Appliance Repair',
    'Roofing',
    'Flooring',
    'HVAC',
    'Tech Support',
    'Tutoring',
    'Beauty Services',
    'Catering',
    'Photography',
    'Other'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleVoiceTranscription = async (transcription) => {
    try {
      // Extract service and description from transcription
      const response = await apiService.classifyService(transcription);
      const classification = response.data.classification;
      
      // Auto-fill form based on transcription
      setFormData(prev => ({
        ...prev,
        service: classification.charAt(0).toUpperCase() + classification.slice(1),
        description: transcription
      }));
      
      setShowVoiceRecorder(false);
    } catch (err) {
      console.error('Error processing voice input:', err);
      setError('Failed to process voice input. Please try again.');
    }
  };

  const handleVoiceError = (errorMessage) => {
    setError(errorMessage);
  };

  const findSmartMatches = async (jobId) => {
    if (!jobId) return;
    
    setSmartMatchLoading(true);
    try {
      // Get smart matches for the job
      const matchResponse = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}/smart-match`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          limit: 10,
          auto_notify: false
        })
      });

      if (matchResponse.ok) {
        const matchData = await matchResponse.json();
        setSmartMatches(matchData.matches || []);
      }

      // Get match insights
      const insightsResponse = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}/match-insights`);
      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setMatchInsights(insightsData.insights);
      }

      setShowSmartMatching(true);
    } catch (err) {
      console.error('Error finding smart matches:', err);
      setError('Failed to find smart matches. Job created successfully.');
    } finally {
      setSmartMatchLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const jobData = {
        ...formData,
        user_id: user.id,
        estimated_price: formData.estimated_price ? parseFloat(formData.estimated_price) : null,
        scheduled_at: formData.scheduled_at ? new Date(formData.scheduled_at).toISOString() : null,
      };

      const response = await apiService.createJob(jobData);
      const jobId = response.data.id;
      setCreatedJobId(jobId);
      
      // Automatically find smart matches after job creation
      await findSmartMatches(jobId);
      
    } catch (err) {
      console.error('Error creating job:', err);
      setError(err.response?.data?.detail || 'Failed to create job');
    } finally {
      setLoading(false);
    }
  };

  const handleNotifyFixers = async () => {
    if (!createdJobId) return;
    
    try {
      const response = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/jobs/${createdJobId}/smart-match`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          limit: 5,
          auto_notify: true
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.notification_result?.success) {
          alert('Top fixers have been notified about your job!');
          navigate(`/jobs/${createdJobId}`);
        }
      }
    } catch (err) {
      console.error('Error notifying fixers:', err);
      setError('Failed to notify fixers');
    }
  };

  const getMatchQualityColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600 bg-green-50';
    if (percentage >= 60) return 'text-blue-600 bg-blue-50';
    if (percentage >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getMatchQualityText = (recommendation) => {
    switch (recommendation) {
      case 'excellent': return '⭐ Excellent Match';
      case 'good': return '👍 Good Match';
      case 'fair': return '👌 Fair Match';
      default: return '⚠️ Poor Match';
    }
  };

  if (showSmartMatching) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">🎯 Smart Matching Results</h1>
              <p className="text-gray-600 mt-1">AI-powered fixer matches for your job</p>
            </div>
            <div className="flex space-x-3">
              <button
                onClick={() => navigate(`/jobs/${createdJobId}`)}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
              >
                View Job Details
              </button>
              {smartMatches.length > 0 && (
                <button
                  onClick={handleNotifyFixers}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                >
                  Notify Top Fixers
                </button>
              )}
            </div>
          </div>

          {smartMatchLoading ? (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                <p className="text-gray-600">Finding the best fixers for your job...</p>
              </div>
            </div>
          ) : (
            <>
              {/* Match Insights */}
              {matchInsights && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <h3 className="font-medium text-blue-900 mb-2">🔍 Matching Insights</h3>
                  <div className="text-sm text-blue-800">
                    <p><strong>Status:</strong> {matchInsights.status}</p>
                    <p><strong>Message:</strong> {matchInsights.message}</p>
                    {matchInsights.total_eligible_fixers && (
                      <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                          <div className="font-semibold text-lg">{matchInsights.total_eligible_fixers}</div>
                          <div className="text-xs">Eligible Fixers</div>
                        </div>
                        <div className="text-center">
                          <div className="font-semibold text-lg">{matchInsights.available_now || 0}</div>
                          <div className="text-xs">Available Now</div>
                        </div>
                        <div className="text-center">
                          <div className="font-semibold text-lg">{matchInsights.highly_rated || 0}</div>
                          <div className="text-xs">Highly Rated</div>
                        </div>
                        <div className="text-center">
                          <div className="font-semibold text-lg">{matchInsights.service_area_coverage || 0}</div>
                          <div className="text-xs">In Your Area</div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Smart Matches */}
              {smartMatches.length > 0 ? (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-4">
                    Top {smartMatches.length} AI-Recommended Fixers
                  </h3>
                  <div className="space-y-4">
                    {smartMatches.map((match, index) => (
                      <div key={match.fixer_id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <h4 className="font-medium text-gray-900">
                                #{index + 1} {match.fixer_name}
                              </h4>
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getMatchQualityColor(match.match_percentage)}`}>
                                {getMatchQualityText(match.recommendation)}
                              </span>
                              <span className="text-sm text-gray-500">
                                {match.match_percentage}% match
                              </span>
                            </div>
                            
                            <p className="text-sm text-gray-600 mb-3">
                              {match.explanation}
                            </p>

                            {/* Score Breakdown */}
                            <div className="grid grid-cols-3 md:grid-cols-6 gap-2 text-xs">
                              <div className="text-center">
                                <div className="font-semibold text-blue-600">{match.factors?.skill_match || 0}</div>
                                <div className="text-gray-500">Skill</div>
                              </div>
                              <div className="text-center">
                                <div className="font-semibold text-green-600">{Math.round(match.factors?.success_rate || 0)}</div>
                                <div className="text-gray-500">Success</div>
                              </div>
                              <div className="text-center">
                                <div className="font-semibold text-purple-600">{Math.round(match.factors?.location_score || 0)}</div>
                                <div className="text-gray-500">Location</div>
                              </div>
                              <div className="text-center">
                                <div className="font-semibold text-orange-600">{Math.round(match.factors?.availability || 0)}</div>
                                <div className="text-gray-500">Available</div>
                              </div>
                              <div className="text-center">
                                <div className="font-semibold text-red-600">{Math.round(match.factors?.reliability || 0)}</div>
                                <div className="text-gray-500">Reliable</div>
                              </div>
                              <div className="text-center">
                                <div className="font-semibold text-indigo-600">{Math.round(match.factors?.fairness_boost || 0)}</div>
                                <div className="text-gray-500">Fair</div>
                              </div>
                            </div>
                          </div>

                          <div className="text-right ml-4">
                            <div className="text-2xl font-bold text-gray-900">
                              {match.match_score}
                            </div>
                            <div className="text-xs text-gray-500">/ 110 points</div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-gray-400 text-6xl mb-4">🔍</div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Perfect Matches Found</h3>
                  <p className="text-gray-600 mb-4">
                    Our AI couldn't find fixers that meet the quality threshold for your specific job requirements.
                  </p>
                  <div className="space-y-2 text-sm text-gray-500">
                    <p>• Try expanding your search area</p>
                    <p>• Consider adjusting service requirements</p>
                    <p>• Check back later as more fixers join the platform</p>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Create New Job</h1>
          <div className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
            ✨ AI-Powered Matching
          </div>
        </div>
        
        {/* Voice Input Toggle */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">How would you like to describe your service?</h2>
            <button
              type="button"
              onClick={() => setShowVoiceRecorder(!showVoiceRecorder)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                showVoiceRecorder 
                  ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                  : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
              <span>{showVoiceRecorder ? 'Hide Voice Input' : 'Use Voice Input'}</span>
            </button>
          </div>
          
          {showVoiceRecorder && (
            <VoiceRecorder
              onTranscription={handleVoiceTranscription}
              onError={handleVoiceError}
            />
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Service */}
          <div>
            <label htmlFor="service" className="block text-sm font-medium text-gray-700 mb-2">
              Service Type *
            </label>
            <select
              id="service"
              name="service"
              required
              value={formData.service}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select a service</option>
              {serviceOptions.map((service) => (
                <option key={service} value={service}>
                  {service}
                </option>
              ))}
            </select>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Job Description *
            </label>
            <textarea
              id="description"
              name="description"
              required
              rows={4}
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe the work that needs to be done..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <p className="mt-1 text-sm text-gray-500">
              💡 You can use the voice input above to describe your service needs in any South African language
            </p>
          </div>

          {/* Location */}
          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
              Location *
            </label>
            <input
              type="text"
              id="location"
              name="location"
              required
              value={formData.location}
              onChange={handleChange}
              placeholder="Enter your address or area"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Estimated Price */}
          <div>
            <label htmlFor="estimated_price" className="block text-sm font-medium text-gray-700 mb-2">
              Estimated Budget (Optional)
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2 text-gray-500">R</span>
              <input
                type="number"
                id="estimated_price"
                name="estimated_price"
                step="0.01"
                min="0"
                value={formData.estimated_price}
                onChange={handleChange}
                placeholder="0.00"
                className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Scheduled Date */}
          <div>
            <label htmlFor="scheduled_at" className="block text-sm font-medium text-gray-700 mb-2">
              Preferred Date & Time (Optional)
            </label>
            <input
              type="datetime-local"
              id="scheduled_at"
              name="scheduled_at"
              value={formData.scheduled_at}
              onChange={handleChange}
              min={new Date().toISOString().slice(0, 16)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
              {error}
            </div>
          )}

          {/* Submit Button */}
          <div className="flex items-center justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/jobs')}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Creating & Finding Matches...</span>
                </div>
              ) : (
                'Create Job with Smart Matching'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateJob;