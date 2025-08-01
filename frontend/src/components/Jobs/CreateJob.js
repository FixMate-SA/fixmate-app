import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import { useNavigate } from 'react-router-dom';
import VoiceRecorder from '../VoiceRecorder/VoiceRecorder';
import TermsAcceptance from '../Workflow/TermsAcceptance';
import { API_BASE_URL } from '../../utils/apiConfig';

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

  useEffect(() => {
    // Check terms acceptance status on component mount
    checkTermsAcceptance();
  }, [user]);

  const checkTermsAcceptance = async () => {
    if (!user?.id) return;

    try {
      const response = await fetch(`${API_BASE_URL}/terms/check/${user.id}`);
      const data = await response.json();
      setTermsAccepted(data.has_accepted);
    } catch (error) {
      console.error('Error checking terms acceptance:', error);
    }
  };

  const handleTermsAcceptance = (accepted) => {
    setTermsAccepted(accepted);
    setShowTermsModal(false);
  };

  const cancelJob = async (jobId) => {
    if (!jobId) return;
    
    setJobBeingCancelled(jobId);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}/cancel`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          cancelled_by: 'client',
          reason: 'Client cancelled service request'
        })
      });

      if (response.ok) {
        setCreatedJobId(null);
        setShowSmartMatching(false);
        alert('Job cancelled successfully. No fees charged.');
      } else {
        const errorData = await response.json();
        alert(`Failed to cancel job: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error cancelling job:', error);
      alert('Failed to cancel job. Please try again.');
    } finally {
      setJobBeingCancelled(null);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleVoiceTranscription = async (transcription) => {
    setFormData(prev => ({ ...prev, description: transcription }));
    setShowVoiceRecorder(false);
  };

  const findSmartMatches = async (jobId) => {
    if (!jobId) return;
    
    setSmartMatchLoading(true);
    try {
      // Get smart matches
      const matchResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}/smart-match`, {
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
      const insightsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}/match-insights`);
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

    // Check if terms are accepted before proceeding
    if (!termsAccepted) {
      setShowTermsModal(true);
      setLoading(false);
      return;
    }

    try {
      const jobData = {
        ...formData,
        user_id: user.id,
        estimated_price: formData.estimated_price ? parseFloat(formData.estimated_price) : null,
        scheduled_at: formData.scheduled_at ? new Date(formData.scheduled_at).toISOString() : null,
        contact_number: user.phone, // Use user's phone as contact
        latitude: null, // TODO: Add GPS integration
        longitude: null
      };

      // Use the enhanced workflow API instead of regular job creation
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/jobs/workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jobData)
      });

      if (response.ok) {
        const responseData = await response.json();
        const jobId = responseData.job_id;
        setCreatedJobId(jobId);
        
        // Show success message with workflow information
        alert(`Job created successfully! ${responseData.message}`);
        
        // Automatically show workflow status
        setShowSmartMatching(true);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create job');
      }
      
    } catch (err) {
      console.error('Error creating job:', err);
      setError('Failed to create job. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleNotifyFixers = async () => {
    if (!createdJobId) return;
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/jobs/${createdJobId}/smart-match`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          auto_notify: true,
          limit: 5
        })
      });

      if (response.ok) {
        alert('Fixers have been notified about your job!');
        // Navigate to job list or dashboard
        navigate('/jobs');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to notify fixers');
      }
    } catch (err) {
      console.error('Error notifying fixers:', err);
      setError('Failed to notify fixers');
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Request a Service</h2>
      
      {/* Terms Acceptance Modal */}
      {showTermsModal && (
        <TermsAcceptance 
          showModal={true}
          onAccept={handleTermsAcceptance}
          onClose={() => setShowTermsModal(false)}
        />
      )}

      {error && (
        <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
          {error}
        </div>
      )}

      {!termsAccepted && (
        <div className="mb-4 p-4 bg-yellow-100 border border-yellow-400 text-yellow-700 rounded">
          ⚠️ You must accept our terms and conditions before creating a job request.
          <button 
            onClick={() => setShowTermsModal(true)}
            className="ml-2 text-blue-600 underline hover:text-blue-800"
          >
            Review Terms
          </button>
        </div>
      )}

      {!showSmartMatching ? (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Service Type *
            </label>
            <select
              name="service"
              value={formData.service}
              onChange={handleChange}
              required
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Select a service</option>
              {serviceOptions.map((service) => (
                <option key={service} value={service}>
                  {service}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description *
            </label>
            <div className="relative">
              <textarea
                name="description"
                value={formData.description}
                onChange={handleChange}
                placeholder="Describe what needs to be fixed or done..."
                required
                rows="4"
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="button"
                onClick={() => setShowVoiceRecorder(true)}
                className="absolute bottom-2 right-2 bg-blue-500 text-white p-2 rounded-full hover:bg-blue-600 transition-colors"
                title="Use voice input"
              >
                🎤
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Location *
            </label>
            <input
              type="text"
              name="location"
              value={formData.location}
              onChange={handleChange}
              placeholder="Enter your location"
              required
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Estimated Budget (R)
            </label>
            <input
              type="number"
              name="estimated_price"
              value={formData.estimated_price}
              onChange={handleChange}
              placeholder="Enter estimated budget"
              min="0"
              step="0.01"
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Preferred Date & Time
            </label>
            <input
              type="datetime-local"
              name="scheduled_at"
              value={formData.scheduled_at}
              onChange={handleChange}
              className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !termsAccepted}
            className={`w-full py-3 px-4 rounded-md font-medium transition-colors ${
              loading || !termsAccepted
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {loading ? 'Creating Job Request...' : 'Submit Job Request'}
          </button>
        </form>
      ) : (
        <div className="space-y-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h3 className="text-lg font-semibold text-green-800 mb-2">
              🎉 Job Request Created Successfully!
            </h3>
            <p className="text-green-700">
              Your job has been created and eligible fixers have been notified via WhatsApp and app notifications.
              The first fixer to accept will get the job (first-come, first-served).
            </p>
          </div>

          {/* Cancel Service Button - System Requirement */}
          <div className="flex gap-4 justify-center">
            <button
              onClick={() => cancelJob(createdJobId)}
              disabled={jobBeingCancelled === createdJobId}
              className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:bg-gray-400"
            >
              {jobBeingCancelled === createdJobId ? 'Cancelling...' : 'Cancel Service'}
            </button>
            
            <button
              onClick={() => navigate('/jobs')}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              View My Jobs
            </button>
          </div>

          {smartMatches.length > 0 && (
            <div className="mt-6">
              <h4 className="text-lg font-semibold mb-3">Available Fixers</h4>
              <div className="grid gap-4">
                {smartMatches.map((match, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h5 className="font-medium">{match.fixer_name}</h5>
                        <p className="text-sm text-gray-600">Rating: {match.rating}/5</p>
                        <p className="text-sm text-gray-600">Match Score: {match.match_score}%</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm text-gray-500">
                          Distance: {match.distance ? `${match.distance}km` : 'N/A'}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {matchInsights && (
            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h4 className="font-semibold text-blue-800 mb-2">Match Insights</h4>
              <div className="text-sm text-blue-700 space-y-1">
                <p>Total Fixers: {matchInsights.total_fixers}</p>
                <p>Eligible Fixers: {matchInsights.eligible_fixers}</p>
                <p>Average Match Score: {matchInsights.average_score}%</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Voice Recorder Modal */}
      {showVoiceRecorder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg max-w-md w-full mx-4">
            <VoiceRecorder 
              onTranscription={handleVoiceTranscription}
              onClose={() => setShowVoiceRecorder(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default CreateJob;