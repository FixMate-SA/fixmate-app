import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import PhotoUploadComponent from '../Common/PhotoUploadComponent';

const EnhancedJobCompletion = () => {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Photo states
  const [beforePhotos, setBeforePhotos] = useState([]);
  const [afterPhotos, setAfterPhotos] = useState([]);
  const [progressPhotos, setProgressPhotos] = useState([]);
  
  // Completion form data
  const [completionData, setCompletionData] = useState({
    finalPrice: '',
    completionNotes: '',
    workDuration: '',
    materialsUsed: '',
    recommendedMaintenance: ''
  });

  const [photoRequirement, setPhotoRequirement] = useState({
    required: false,
    reason: ''
  });

  useEffect(() => {
    fetchJobDetails();
  }, [jobId]);

  const fetchJobDetails = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}`);
      if (response.ok) {
        const jobData = await response.json();
        setJob(jobData);
        
        // Pre-fill estimated price as final price
        if (jobData.estimated_price) {
          setCompletionData(prev => ({
            ...prev,
            finalPrice: jobData.estimated_price.toString()
          }));
        }
        
        // Check if photos are required
        checkPhotoRequirement(jobData);
        
        // Load existing photos if any
        loadExistingPhotos();
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

  const checkPhotoRequirement = (jobData) => {
    // Determine if photos are required based on job type, value, etc.
    const highValueJobs = ['plumbing', 'electrical', 'painting', 'carpentry'];
    const isHighValue = jobData.estimated_price >= 1000;
    const requiresPhotos = highValueJobs.includes(jobData.service?.toLowerCase()) || isHighValue;
    
    let reason = '';
    if (isHighValue) reason = 'High-value job (R1000+)';
    else if (highValueJobs.includes(jobData.service?.toLowerCase())) reason = 'Service type requires verification';
    
    setPhotoRequirement({
      required: requiresPhotos,
      reason: reason
    });
  };

  const loadExistingPhotos = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}/photo-verification`);
      if (response.ok) {
        const data = await response.json();
        if (data.verification) {
          // Load existing photos if available (implementation would depend on backend structure)
          console.log('Existing photo verification:', data.verification);
        }
      }
    } catch (err) {
      console.error('Error loading existing photos:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCompletionData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!completionData.finalPrice) {
      setError('Final price is required');
      return;
    }

    if (photoRequirement.required && afterPhotos.length === 0) {
      setError('After photos are required for this job type');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      // Prepare photo data for submission
      const beforePhotosData = beforePhotos.map(photo => photo.data);
      const afterPhotosData = afterPhotos.map(photo => photo.data);
      const progressPhotosData = progressPhotos.map(photo => photo.data);

      const completionPayload = {
        final_price: parseFloat(completionData.finalPrice),
        completion_notes: completionData.completionNotes,
        work_duration: completionData.workDuration ? parseInt(completionData.workDuration) : null,
        materials_used: completionData.materialsUsed,
        recommended_maintenance: completionData.recommendedMaintenance,
        before_photos: beforePhotosData,
        after_photos: afterPhotosData,
        progress_photos: progressPhotosData
      };

      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}/complete-with-photos`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify(completionPayload)
        }
      );

      if (response.ok) {
        const result = await response.json();
        setSuccess('Job completed successfully with photo verification!');
        
        // Redirect after a short delay
        setTimeout(() => {
          navigate(`/jobs/${jobId}`);
        }, 2000);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to complete job');
      }
    } catch (err) {
      console.error('Error completing job:', err);
      setError('Error completing job. Please try again.');
    } finally {
      setSubmitting(false);
    }
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
        Job not found
      </div>
    );
  }

  // Check if user is authorized to complete this job
  if (job.fixer_id !== user?.id) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
        You are not authorized to complete this job.
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-3 mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Complete Job with Photo Verification</h1>
          {photoRequirement.required && (
            <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2 py-1 rounded-full">
              📸 Photos Required
            </span>
          )}
        </div>

        {/* Job Details Summary */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h2 className="text-lg font-medium text-gray-900 mb-3">Job Summary</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium text-gray-700">Service:</span>
              <span className="ml-2">{job.service}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Location:</span>
              <span className="ml-2">{job.location}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Client:</span>
              <span className="ml-2">{job.user?.display_name || 'Unknown'}</span>
            </div>
            <div>
              <span className="font-medium text-gray-700">Estimated Price:</span>
              <span className="ml-2">R{job.estimated_price || 'Not specified'}</span>
            </div>
          </div>
          <div className="mt-3">
            <span className="font-medium text-gray-700">Description:</span>
            <p className="mt-1 text-gray-600">{job.description}</p>
          </div>
        </div>

        {/* Photo Requirement Notice */}
        {photoRequirement.required && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div className="flex items-start space-x-3">
              <span className="text-2xl">📸</span>
              <div>
                <h3 className="font-medium text-blue-900">Photo Verification Required</h3>
                <p className="text-sm text-blue-800 mt-1">
                  This job requires before and after photos for verification. 
                  <br />Reason: {photoRequirement.reason}
                </p>
              </div>
            </div>
          </div>
        )}

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
          {/* Photo Upload Sections */}
          <div className="space-y-8">
            {/* Before Photos */}
            <PhotoUploadComponent
              photoType="before"
              maxPhotos={5}
              onPhotosChange={setBeforePhotos}
              existingPhotos={beforePhotos}
              disabled={submitting}
              required={false}
            />

            {/* Progress Photos */}
            <PhotoUploadComponent
              photoType="progress"
              maxPhotos={10}
              onPhotosChange={setProgressPhotos}
              existingPhotos={progressPhotos}
              disabled={submitting}
              required={false}
            />

            {/* After Photos */}
            <PhotoUploadComponent
              photoType="after"
              maxPhotos={5}
              onPhotosChange={setAfterPhotos}
              existingPhotos={afterPhotos}
              disabled={submitting}
              required={photoRequirement.required}
            />
          </div>

          {/* Completion Details */}
          <div className="bg-gray-50 rounded-lg p-6 space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Job Completion Details</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Final Price */}
              <div>
                <label htmlFor="finalPrice" className="block text-sm font-medium text-gray-700 mb-2">
                  Final Price (R) *
                </label>
                <input
                  type="number"
                  id="finalPrice"
                  name="finalPrice"
                  step="0.01"
                  min="0"
                  required
                  value={completionData.finalPrice}
                  onChange={handleInputChange}
                  disabled={submitting}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Work Duration */}
              <div>
                <label htmlFor="workDuration" className="block text-sm font-medium text-gray-700 mb-2">
                  Actual Work Duration (minutes)
                </label>
                <input
                  type="number"
                  id="workDuration"
                  name="workDuration"
                  min="0"
                  value={completionData.workDuration}
                  onChange={handleInputChange}
                  disabled={submitting}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Completion Notes */}
            <div>
              <label htmlFor="completionNotes" className="block text-sm font-medium text-gray-700 mb-2">
                Completion Notes *
              </label>
              <textarea
                id="completionNotes"
                name="completionNotes"
                rows={4}
                required
                value={completionData.completionNotes}
                onChange={handleInputChange}
                disabled={submitting}
                placeholder="Describe the work completed, any issues encountered, and final results..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Materials Used */}
            <div>
              <label htmlFor="materialsUsed" className="block text-sm font-medium text-gray-700 mb-2">
                Materials/Parts Used
              </label>
              <textarea
                id="materialsUsed"
                name="materialsUsed"
                rows={3}
                value={completionData.materialsUsed}
                onChange={handleInputChange}
                disabled={submitting}
                placeholder="List any materials, parts, or components used..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Recommended Maintenance */}
            <div>
              <label htmlFor="recommendedMaintenance" className="block text-sm font-medium text-gray-700 mb-2">
                Recommended Maintenance
              </label>
              <textarea
                id="recommendedMaintenance"
                name="recommendedMaintenance"
                rows={3}
                value={completionData.recommendedMaintenance}
                onChange={handleInputChange}
                disabled={submitting}
                placeholder="Any maintenance recommendations for the client..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
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
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Completing Job...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Complete Job with Photos</span>
                </div>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EnhancedJobCompletion;