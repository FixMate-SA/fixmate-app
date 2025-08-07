import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/api';
import { useNavigate } from 'react-router-dom';
import VoiceRecorder from '../VoiceRecorder/VoiceRecorder';

const CreateJob = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [jobData, setJobData] = useState({
    title: '',
    description: '',
    location: '',
    urgency: 'medium',
    budget_min: '',
    budget_max: '',
    preferred_date: '',
    preferred_time: '',
    category: '',
    images: [],
    communication_preference: 'phone',
    whatsapp_notifications: true
  });

  const categories = [
    { value: 'plumbing', label: t('plumbing', 'Plumbing') },
    { value: 'electrical', label: t('electrical', 'Electrical') },
    { value: 'carpentry', label: t('carpentry', 'Carpentry') },
    { value: 'painting', label: t('painting', 'Painting') },
    { value: 'gardening', label: t('gardening', 'Gardening') },
    { value: 'cleaning', label: t('cleaning', 'Cleaning') },
    { value: 'appliance_repair', label: t('applianceRepair', 'Appliance Repair') },
    { value: 'other', label: t('other', 'Other') }
  ];

  const urgencyLevels = [
    { value: 'low', label: t('low', 'Low'), color: 'text-green-600' },
    { value: 'medium', label: t('medium', 'Medium'), color: 'text-yellow-600' },
    { value: 'high', label: t('high', 'High'), color: 'text-orange-600' },
    { value: 'urgent', label: t('urgent', 'Urgent'), color: 'text-red-600' }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setJobData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    files.forEach(file => {
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = (e) => {
          setJobData(prev => ({
            ...prev,
            images: [...prev.images, e.target.result]
          }));
        };
        reader.readAsDataURL(file);
      }
    });
  };

  const removeImage = (index) => {
    setJobData(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }));
  };

  const handleVoiceTranscription = (transcription) => {
    setJobData(prev => ({
      ...prev,
      description: prev.description + ' ' + transcription
    }));
  };

  const handleVoiceError = (error) => {
    console.error('Voice recording error:', error);
    setError(t('voiceRecordingError', 'Voice recording failed. Please try again.'));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!jobData.title.trim() || !jobData.description.trim()) {
      setError(t('titleDescriptionRequired', 'Title and description are required'));
      return;
    }

    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const jobDataToSubmit = {
        ...jobData,
        client_id: user.id,
        budget_min: parseFloat(jobData.budget_min) || 0,
        budget_max: parseFloat(jobData.budget_max) || 0
      };

      const response = await apiService.createJob(jobDataToSubmit);
      
      setSuccess(t('jobCreatedSuccessfully', 'Job created successfully! You will be notified when fixers apply.'));
      
      // Reset form
      setJobData({
        title: '',
        description: '',
        location: '',
        urgency: 'medium',
        budget_min: '',
        budget_max: '',
        preferred_date: '',
        preferred_time: '',
        category: '',
        images: []
      });

      // Navigate to job list after a delay
      setTimeout(() => {
        navigate('/jobs/list');
      }, 2000);

    } catch (err) {
      console.error('Job creation error:', err);
      setError(err.response?.data?.detail || t('jobCreationError', 'Failed to create job. Please try again.'));
    }

    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-md p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          {t('createNewJob')}
        </h1>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div className="text-sm text-red-600">{error}</div>
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 rounded-md p-4 mb-6">
            <div className="text-sm text-green-600">{success}</div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Job Title */}
          <div>
            <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
              {t('jobTitle')} <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={jobData.title}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder={t('enterJobTitle', 'Enter a clear, descriptive title')}
              required
            />
          </div>

          {/* Category */}
          <div>
            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
              {t('category')}
            </label>
            <select
              id="category"
              name="category"
              value={jobData.category}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">{t('selectCategory', 'Select a category')}</option>
              {categories.map(cat => (
                <option key={cat.value} value={cat.value}>{cat.label}</option>
              ))}
            </select>
          </div>

          {/* Job Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              {t('jobDescription')} <span className="text-red-500">*</span>
            </label>
            <textarea
              id="description"
              name="description"
              value={jobData.description}
              onChange={handleInputChange}
              rows="5"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder={t('describeJobDetails', 'Describe the job in detail - what needs to be done, any specific requirements, etc.')}
              required
            />
            
            {/* Voice Recorder */}
            <div className="mt-2">
              <VoiceRecorder 
                onTranscription={handleVoiceTranscription}
                onError={handleVoiceError}
              />
            </div>
          </div>

          {/* Location */}
          <div>
            <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
              {t('location')}
            </label>
            <input
              type="text"
              id="location"
              name="location"
              value={jobData.location}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder={t('enterLocation', 'Enter the job location')}
            />
          </div>

          {/* Urgency */}
          <div>
            <label htmlFor="urgency" className="block text-sm font-medium text-gray-700 mb-2">
              {t('urgency')}
            </label>
            <select
              id="urgency"
              name="urgency"
              value={jobData.urgency}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {urgencyLevels.map(level => (
                <option key={level.value} value={level.value}>{level.label}</option>
              ))}
            </select>
          </div>

          {/* Budget Range */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="budget_min" className="block text-sm font-medium text-gray-700 mb-2">
                {t('minimumBudget')}
              </label>
              <input
                type="number"
                id="budget_min"
                name="budget_min"
                value={jobData.budget_min}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="0"
                min="0"
              />
            </div>
            <div>
              <label htmlFor="budget_max" className="block text-sm font-medium text-gray-700 mb-2">
                {t('maximumBudget')}
              </label>
              <input
                type="number"
                id="budget_max"
                name="budget_max"
                value={jobData.budget_max}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="0"
                min="0"
              />
            </div>
          </div>

          {/* Preferred Date & Time */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label htmlFor="preferred_date" className="block text-sm font-medium text-gray-700 mb-2">
                {t('preferredDate')}
              </label>
              <input
                type="date"
                id="preferred_date"
                name="preferred_date"
                value={jobData.preferred_date}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label htmlFor="preferred_time" className="block text-sm font-medium text-gray-700 mb-2">
                {t('preferredTime')}
              </label>
              <input
                type="time"
                id="preferred_time"
                name="preferred_time"
                value={jobData.preferred_time}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Image Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('jobImages')}
            </label>
            <input
              type="file"
              multiple
              accept="image/*"
              onChange={handleImageUpload}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            
            {/* Image Preview */}
            {jobData.images.length > 0 && (
              <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-4">
                {jobData.images.map((image, index) => (
                  <div key={index} className="relative">
                    <img
                      src={image}
                      alt={`${t('jobImage')} ${index + 1}`}
                      className="w-full h-32 object-cover rounded-md"
                    />
                    <button
                      type="button"
                      onClick={() => removeImage(index)}
                      className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex items-center justify-between pt-6">
            <button
              type="button"
              onClick={() => navigate('/client/dashboard')}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {t('cancel')}
            </button>
            
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-300 disabled:cursor-not-allowed"
            >
              {loading ? t('creating', 'Creating...') : t('createJob')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateJob;