import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import PhotoUploadComponent from '../Common/PhotoUploadComponent';

const DisputeCreation = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const [evidencePhotos, setEvidencePhotos] = useState([]);
  
  const [disputeData, setDisputeData] = useState({
    disputeType: '',
    description: '',
    priorityLevel: 'normal',
    evidenceDescription: ''
  });

  const disputeTypes = [
    { value: 'quality', label: 'Work Quality Issues', description: 'Poor workmanship or unsatisfactory results' },
    { value: 'no_show', label: 'Fixer No Show', description: 'Fixer did not arrive as scheduled' },
    { value: 'incomplete', label: 'Incomplete Work', description: 'Job was not completed as agreed' },
    { value: 'damage', label: 'Property Damage', description: 'Damage occurred during the service' },
    { value: 'behavior', label: 'Unprofessional Behavior', description: 'Inappropriate or unprofessional conduct' },
    { value: 'payment', label: 'Payment Issues', description: 'Disputes about pricing or payment' },
    { value: 'timing', label: 'Scheduling Issues', description: 'Problems with timing or delays' },
    { value: 'other', label: 'Other Issues', description: 'Other concerns not listed above' }
  ];

  const priorityLevels = [
    { value: 'low', label: 'Low Priority', description: 'Minor issue, no urgency' },
    { value: 'normal', label: 'Normal Priority', description: 'Standard issue requiring attention' },
    { value: 'high', label: 'High Priority', description: 'Significant issue requiring prompt attention' },
    { value: 'urgent', label: 'Urgent', description: 'Critical issue requiring immediate attention' }
  ];

  useEffect(() => {
    fetchJobDetails();
  }, [jobId]);

  const fetchJobDetails = async () => {
    try {
      const response = await fetch(`${import.meta.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}`);
      if (response.ok) {
        const jobData = await response.json();
        setJob(jobData);
        
        // Check if user is authorized to create dispute for this job
        const isAuthorized = (
          jobData.user_id === user?.id || // Client
          jobData.fixer_id === user?.id || // Fixer
          user?.role === 'admin' // Admin
        );
        
        if (!isAuthorized) {
          setError('You are not authorized to create a dispute for this job.');
        }
      } else {
        setError('Failed to load job details');
      }
    } catch (err) {
      console.error('Error fetching job:', err);
      setError('Error loading job details');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setDisputeData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!disputeData.disputeType) {
      setError('Please select a dispute type');
      return;
    }

    if (!disputeData.description.trim()) {
      setError('Please provide a detailed description of the issue');
      return;
    }

    if (disputeData.description.trim().length < 20) {
      setError('Please provide a more detailed description (at least 20 characters)');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      // Prepare evidence photos
      const evidencePhotosData = evidencePhotos.map(photo => photo.data);

      const disputePayload = {
        dispute_type: disputeData.disputeType,
        description: disputeData.description.trim(),
        priority_level: disputeData.priorityLevel,
        evidence_description: disputeData.evidenceDescription.trim(),
        evidence_photos: evidencePhotosData
      };

      const response = await fetch(
        `${import.meta.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}/dispute`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(disputePayload)
        }
      );

      if (response.ok) {
        const result = await response.json();
        setSuccess('Dispute created successfully! An admin will review your case shortly.');
        
        // Redirect after a short delay
        setTimeout(() => {
          navigate(`/disputes/${result.dispute_id}`);
        }, 2000);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to create dispute');
      }
    } catch (err) {
      console.error('Error creating dispute:', err);
      setError('Error creating dispute. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const getDisputeTypeIcon = (type) => {
    const icons = {
      quality: '⚠️',
      no_show: '❌',
      incomplete: '🔄',
      damage: '💥',
      behavior: '👤',
      payment: '💰',
      timing: '⏰',
      other: '❓'
    };
    return icons[type] || '📋';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      low: 'border-gray-300 bg-gray-50',
      normal: 'border-blue-300 bg-blue-50',
      high: 'border-yellow-300 bg-yellow-50',
      urgent: 'border-red-300 bg-red-50'
    };
    return colors[priority] || 'border-gray-300 bg-gray-50';
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
        Job not found or you don't have permission to access it.
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Create Dispute</h1>
          <span className="bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded-full">
            ⚖️ Formal Resolution Process
          </span>
        </div>

        {/* Job Details Summary */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-3">Job Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Service:</span>
              <span className="ml-2">{job.service}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Status:</span>
              <span className="ml-2 capitalize">{job.status}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Location:</span>
              <span className="ml-2">{job.location}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Final Price:</span>
              <span className="ml-2">R{job.final_price || job.estimated_price || 'Not specified'}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Client:</span>
              <span className="ml-2">{job.user?.display_name || 'Unknown'}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Fixer:</span>
              <span className="ml-2">{job.fixer?.name || 'Not assigned'}</span>
            </div>
          </div>
        </div>

        {/* Important Notice */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
          <div className="flex items-start space-x-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <h3 className="font-medium text-yellow-900">Important Information</h3>
              <ul className="text-sm text-yellow-800 mt-2 space-y-1">
                <li>• Disputes are formal processes reviewed by our admin team</li>
                <li>• Payment may be held during dispute resolution if necessary</li>
                <li>• All parties will have the opportunity to present their case</li>
                <li>• False or frivolous disputes may result in account penalties</li>
                <li>• Try to resolve issues directly with the other party first</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md mb-6">
            {success}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Dispute Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-4">
              What type of issue are you reporting? *
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {disputeTypes.map((type) => (
                <label
                  key={type.value}
                  className={`relative cursor-pointer rounded-lg border p-4 transition-colors hover:border-blue-400 ${
                    disputeData.disputeType === type.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 bg-white'
                  }`}
                >
                  <input
                    type="radio"
                    name="disputeType"
                    value={type.value}
                    checked={disputeData.disputeType === type.value}
                    onChange={handleInputChange}
                    disabled={submitting}
                    className="sr-only"
                  />
                  <div className="flex items-start space-x-3">
                    <span className="text-xl">{getDisputeTypeIcon(type.value)}</span>
                    <div>
                      <div className="font-medium text-gray-900">{type.label}</div>
                      <div className="text-sm text-gray-600">{type.description}</div>
                    </div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Priority Level */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-4">
              Priority Level *
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {priorityLevels.map((priority) => (
                <label
                  key={priority.value}
                  className={`relative cursor-pointer rounded-lg border p-3 transition-colors hover:border-gray-400 ${
                    disputeData.priorityLevel === priority.value
                      ? 'border-blue-500 bg-blue-50'
                      : getPriorityColor(priority.value)
                  }`}
                >
                  <input
                    type="radio"
                    name="priorityLevel"
                    value={priority.value}
                    checked={disputeData.priorityLevel === priority.value}
                    onChange={handleInputChange}
                    disabled={submitting}
                    className="sr-only"
                  />
                  <div>
                    <div className="font-medium text-gray-900">{priority.label}</div>
                    <div className="text-sm text-gray-600">{priority.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* Detailed Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Detailed Description *
            </label>
            <textarea
              id="description"
              name="description"
              rows={6}
              required
              value={disputeData.description}
              onChange={handleInputChange}
              disabled={submitting}
              placeholder="Please provide a detailed description of the issue, including:
- What happened?
- When did it occur?
- What was expected vs. what actually happened?
- Any attempts to resolve the issue?
- Impact on you or your property?"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <div className="mt-1 text-sm text-gray-500">
              {disputeData.description.length}/500 characters (minimum 20)
            </div>
          </div>

          {/* Evidence Photos */}
          <div>
            <PhotoUploadComponent
              photoType="evidence"
              maxPhotos={8}
              onPhotosChange={setEvidencePhotos}
              existingPhotos={evidencePhotos}
              disabled={submitting}
              required={false}
            />
          </div>

          {/* Evidence Description */}
          <div>
            <label htmlFor="evidenceDescription" className="block text-sm font-medium text-gray-700 mb-2">
              Evidence Description
            </label>
            <textarea
              id="evidenceDescription"
              name="evidenceDescription"
              rows={3}
              value={disputeData.evidenceDescription}
              onChange={handleInputChange}
              disabled={submitting}
              placeholder="Describe any photos or evidence you've provided..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Submit Button */}
          <div className="flex items-center justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate(`/jobs/${jobId}`)}
              disabled={submitting}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 disabled:opacity-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-6 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Creating Dispute...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <span>Create Dispute</span>
                </div>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DisputeCreation;