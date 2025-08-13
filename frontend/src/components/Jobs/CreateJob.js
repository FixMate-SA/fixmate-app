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
    const { name, value, type, checked } = e.target;
    setJobData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
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
      
      // Trigger dashboard refresh across tabs/windows
      localStorage.setItem('fixmate_dashboard_refresh', Date.now().toString());
      
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

          {/* Communication Preferences */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
              <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 24 24">
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.297"/>
              </svg>
              {t('communicationPreferences', 'Communication Preferences')}
            </h3>
            
            {/* Preferred Communication Method */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('preferredContactMethod', 'Preferred Contact Method')}
              </label>
              <select
                name="communication_preference"
                value={jobData.communication_preference}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="phone">{t('phone', 'Phone Call')}</option>
                <option value="whatsapp">{t('whatsapp', 'WhatsApp')}</option>
                <option value="sms">{t('sms', 'SMS')}</option>
                <option value="email">{t('email', 'Email')}</option>
              </select>
            </div>

            {/* WhatsApp Notifications */}
            <div className="flex items-center">
              <input
                type="checkbox"
                id="whatsapp_notifications"
                name="whatsapp_notifications"
                checked={jobData.whatsapp_notifications}
                onChange={handleInputChange}
                className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
              />
              <label htmlFor="whatsapp_notifications" className="ml-2 text-sm text-gray-700 flex items-center gap-2">
                <span>{t('enableWhatsAppNotifications', 'Enable WhatsApp notifications for job updates')}</span>
                <span className="text-xs text-gray-500 bg-green-100 px-2 py-1 rounded">
                  📱 +27 75 446 6571
                </span>
              </label>
            </div>
            
            <p className="text-xs text-gray-500 mt-2">
              {t('communicationNote', 'Fixers will be notified about your preferences. WhatsApp notifications are recommended for faster responses.')}
            </p>
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