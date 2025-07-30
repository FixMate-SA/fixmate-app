import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import TermsAcceptance from './TermsAcceptance';
import JobWorkflowStatus from './JobWorkflowStatus';

const EnhancedJobCreation = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  
  const [currentStep, setCurrentStep] = useState(1);
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [jobData, setJobData] = useState({
    service: '',
    description: '',
    location: '',
    estimated_price: '',
    contact_number: ''
  });
  const [loading, setLoading] = useState(false);
  const [createdJob, setCreatedJob] = useState(null);
  const [workflowStatus, setWorkflowStatus] = useState(null);

  useEffect(() => {
    // Check terms acceptance on component mount
    checkTermsAcceptance();
  }, []);

  const checkTermsAcceptance = async () => {
    if (!user?.id) return;

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/terms/check/${user.id}`);
      const data = await response.json();
      setTermsAccepted(data.has_accepted);
    } catch (error) {
      console.error('Error checking terms:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setJobData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleNext = () => {
    if (currentStep === 1 && !termsAccepted) {
      setShowTermsModal(true);
      return;
    }
    
    if (validateStep(currentStep)) {
      setCurrentStep(prev => prev + 1);
    }
  };

  const validateStep = (step) => {
    switch (step) {
      case 1: // Terms & Service
        return termsAccepted && jobData.service.trim() !== '';
      case 2: // Description
        return jobData.description.trim().length >= 10;
      case 3: // Location & Contact
        return jobData.location.trim() !== '' && jobData.contact_number.trim() !== '';
      default:
        return true;
    }
  };

  const handleSubmit = async () => {
    if (!validateStep(3)) return;

    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/jobs/workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...jobData,
          user_id: user.id,
          estimated_price: jobData.estimated_price ? parseFloat(jobData.estimated_price) : null
        })
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setCreatedJob(result);
        setWorkflowStatus(result.workflow_status);
        setCurrentStep(4); // Success step
      } else {
        throw new Error(result.message || 'Failed to create job');
      }
    } catch (error) {
      console.error('Error creating job:', error);
      alert(error.message || 'Failed to create job. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleTermsAccepted = (accepted) => {
    setTermsAccepted(accepted);
    setShowTermsModal(false);
    if (accepted && currentStep === 1) {
      setCurrentStep(2);
    }
  };

  const resetForm = () => {
    setCurrentStep(1);
    setJobData({
      service: '',
      description: '',
      location: '',
      estimated_price: '',
      contact_number: ''
    });
    setCreatedJob(null);
    setWorkflowStatus(null);
  };

  const renderStepIndicator = () => (
    <div className="mb-8">
      <div className="flex items-center justify-center">
        {[1, 2, 3, 4].map((step, index) => (
          <React.Fragment key={step}>
            <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
              step <= currentStep 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-600'
            }`}>
              {step < currentStep ? '✓' : step}
            </div>
            {index < 3 && (
              <div className={`h-1 w-8 mx-2 ${
                step < currentStep ? 'bg-blue-600' : 'bg-gray-200'
              }`}></div>
            )}
          </React.Fragment>
        ))}
      </div>
      <div className="flex justify-between mt-2 text-xs text-gray-600">
        <span>Terms</span>
        <span>Details</span>
        <span>Location</span>
        <span>Confirm</span>
      </div>
    </div>
  );

  const renderStep1 = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-center mb-6">
        🔧 {t('createServiceRequest', 'Create Service Request')}
      </h2>

      {!termsAccepted && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              ⚖️
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                {t('termsAcceptanceRequired', 'Terms Acceptance Required')}
              </h3>
              <p className="mt-1 text-sm text-yellow-700">
                {t('mustAcceptTerms', 'You must accept our platform terms before creating a service request.')}
              </p>
              <button
                onClick={() => setShowTermsModal(true)}
                className="mt-2 text-sm text-yellow-800 underline hover:text-yellow-900"
              >
                {t('reviewTerms', 'Review & Accept Terms')}
              </button>
            </div>
          </div>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('serviceType', 'Service Type')} *
        </label>
        <select
          name="service"
          value={jobData.service}
          onChange={handleInputChange}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        >
          <option value="">{t('selectService', 'Select a service...')}</option>
          <option value="plumbing">{t('plumbing', 'Plumbing')}</option>
          <option value="electrical">{t('electrical', 'Electrical')}</option>
          <option value="carpentry">{t('carpentry', 'Carpentry')}</option>
          <option value="painting">{t('painting', 'Painting')}</option>
          <option value="cleaning">{t('cleaning', 'Cleaning')}</option>
          <option value="gardening">{t('gardening', 'Gardening')}</option>
          <option value="appliance_repair">{t('applianceRepair', 'Appliance Repair')}</option>
          <option value="handyman">{t('handyman', 'General Handyman')}</option>
        </select>
      </div>

      <button
        onClick={handleNext}
        disabled={!termsAccepted || !jobData.service}
        className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
          termsAccepted && jobData.service
            ? 'bg-blue-600 hover:bg-blue-700 text-white'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        }`}
      >
        {t('continue', 'Continue')}
      </button>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-center">
        📝 {t('describeYourProblem', 'Describe Your Problem')}
      </h2>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('detailedDescription', 'Detailed Description')} *
        </label>
        <textarea
          name="description"
          value={jobData.description}
          onChange={handleInputChange}
          rows={5}
          placeholder={t('descriptionPlaceholder', 'Describe the issue in detail. What needs to be fixed or done? When did the problem start? Any specific requirements?')}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
        <p className="mt-1 text-xs text-gray-500">
          {jobData.description.length}/200 characters minimum (10 required)
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('estimatedBudget', 'Estimated Budget (Optional)')}
        </label>
        <div className="relative">
          <span className="absolute left-3 top-2 text-gray-500">R</span>
          <input
            type="number"
            name="estimated_price"
            value={jobData.estimated_price}
            onChange={handleInputChange}
            placeholder="0.00"
            min="0"
            step="0.01"
            className="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      <div className="flex space-x-3">
        <button
          onClick={() => setCurrentStep(1)}
          className="flex-1 py-3 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          {t('back', 'Back')}
        </button>
        <button
          onClick={handleNext}
          disabled={jobData.description.trim().length < 10}
          className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
            jobData.description.trim().length >= 10
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {t('continue', 'Continue')}
        </button>
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-center">
        📍 {t('locationAndContact', 'Location & Contact')}
      </h2>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('location', 'Location')} *
        </label>
        <input
          type="text"
          name="location"
          value={jobData.location}
          onChange={handleInputChange}
          placeholder={t('locationPlaceholder', 'e.g., 123 Main Street, Cape Town, Western Cape')}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {t('contactNumber', 'Contact Number')} *
        </label>
        <input
          type="tel"
          name="contact_number"
          value={jobData.contact_number}
          onChange={handleInputChange}
          placeholder="+27821234567"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
        <p className="mt-1 text-xs text-gray-500">
          {t('contactNumberHelp', 'Fixers will use this number to contact you about the job')}
        </p>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-blue-800 mb-2">
          🎯 {t('whatHappensNext', 'What happens next?')}
        </h3>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• {t('nextStep1', 'Eligible fixers will be notified immediately')}</li>
          <li>• {t('nextStep2', 'First fixer to accept gets the job')}</li>
          <li>• {t('nextStep3', 'You can track their location in real-time')}</li>
          <li>• {t('nextStep4', 'R20 platform fee applies per completed job')}</li>
        </ul>
      </div>

      <div className="flex space-x-3">
        <button
          onClick={() => setCurrentStep(2)}
          className="flex-1 py-3 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          {t('back', 'Back')}
        </button>
        <button
          onClick={handleSubmit}
          disabled={loading || !jobData.location.trim() || !jobData.contact_number.trim()}
          className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
            !loading && jobData.location.trim() && jobData.contact_number.trim()
              ? 'bg-green-600 hover:bg-green-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              {t('creating', 'Creating...')}
            </div>
          ) : (
            t('createJobRequest', 'Create Job Request')
          )}
        </button>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="space-y-6">
      <div className="text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          🎉 {t('jobCreated', 'Job Request Created!')}
        </h2>
        <p className="text-gray-600">
          {t('jobCreatedMessage', 'Your service request has been created and fixers are being notified.')}
        </p>
      </div>

      {workflowStatus && (
        <JobWorkflowStatus 
          jobId={createdJob?.job_id} 
          initialStatus={workflowStatus} 
        />
      )}

      <div className="flex space-x-3">
        <button
          onClick={resetForm}
          className="flex-1 py-3 px-4 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          {t('createAnother', 'Create Another Job')}
        </button>
        <button
          onClick={() => window.location.href = '/jobs'}
          className="flex-1 py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
        >
          {t('viewAllJobs', 'View All Jobs')}
        </button>
      </div>
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto p-6">
      {renderStepIndicator()}

      <div className="bg-white rounded-lg shadow-sm p-6">
        {currentStep === 1 && renderStep1()}
        {currentStep === 2 && renderStep2()}
        {currentStep === 3 && renderStep3()}
        {currentStep === 4 && renderStep4()}
      </div>

      {showTermsModal && (
        <TermsAcceptance
          showModal={true}
          onAccept={handleTermsAccepted}
          onClose={() => setShowTermsModal(false)}
        />
      )}
    </div>
  );
};

export default EnhancedJobCreation;