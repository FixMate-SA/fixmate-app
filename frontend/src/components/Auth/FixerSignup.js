import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { getApiUrl } from '../../utils/api';
import Logo from '../Common/Logo';

const FixerSignup = () => {
  const { login } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    phone: '',
    first_name: '',
    last_name: '',
    id_number: '',
    town: '',
    email: '',
    password: '',
    confirm_password: '',
    // Fixer-specific fields
    services_offered: '',
    experience_years: '',
    qualifications: '',
    previous_work: '',
    why_fixer: '',
    // Document uploads (base64)
    id_document: '',
    proof_of_address: '',
    qualifications_cert: '',
    criminal_clearance: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentStep, setCurrentStep] = useState(1);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileUpload = (fieldName, file) => {
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setFormData(prev => ({
          ...prev,
          [fieldName]: e.target.result
        }));
      };
      reader.readAsDataURL(file);
    }
  };

  const validateStep1 = () => {
    const { phone, first_name, last_name, id_number, town } = formData;
    
    if (!phone.trim()) {
      setError('Phone number is required');
      return false;
    }
    if (!first_name.trim()) {
      setError('First name is required');
      return false;
    }
    if (!last_name.trim()) {
      setError('Last name is required');
      return false;
    }
    if (!id_number.trim()) {
      setError('ID number is required');
      return false;
    }
    if (id_number.length !== 13) {
      setError('South African ID number must be 13 digits');
      return false;
    }
    if (!town.trim()) {
      setError('Town/Municipality is required');
      return false;
    }
    
    return true;
  };

  const validateStep2 = () => {
    const { services_offered, experience_years, why_fixer } = formData;
    
    if (!services_offered.trim()) {
      setError('Please specify the services you offer');
      return false;
    }
    if (!experience_years.trim()) {
      setError('Please specify your years of experience');
      return false;
    }
    if (!why_fixer.trim()) {
      setError('Please tell us why you want to be a fixer');
      return false;
    }
    
    return true;
  };

  const validateStep3 = () => {
    const { password, confirm_password } = formData;
    
    if (!password) {
      setError('Password is required');
      return false;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return false;
    }
    if (password !== confirm_password) {
      setError('Passwords do not match');
      return false;
    }
    
    return true;
  };

  const handleNextStep = () => {
    setError('');
    if (currentStep === 1 && validateStep1()) {
      setCurrentStep(2);
    } else if (currentStep === 2 && validateStep2()) {
      setCurrentStep(3);
    }
  };

  const handlePreviousStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!validateStep3()) {
      setLoading(false);
      return;
    }

    try {
      // First create the basic user account
      const userResponse = await fetch(getApiUrl('/auth/signup'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: formData.phone,
          first_name: formData.first_name,
          last_name: formData.last_name,
          id_number: formData.id_number,
          town: formData.town,
          email: formData.email,
          password: formData.password,
          confirm_password: formData.confirm_password
        }),
      });

      const userData = await userResponse.json();

      if (userResponse.ok && userData.user) {
        // Submit fixer application
        const applicationResponse = await fetch(getApiUrl('/fixer/apply'), {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            services_offered: formData.services_offered,
            experience_years: parseInt(formData.experience_years) || 0,
            qualifications: formData.qualifications,
            previous_work: formData.previous_work,
            why_fixer: formData.why_fixer,
            id_document: formData.id_document,
            proof_of_address: formData.proof_of_address,
            qualifications_cert: formData.qualifications_cert,
            criminal_clearance: formData.criminal_clearance,
            user_id: userData.user.id
          }),
        });

        const applicationData = await applicationResponse.json();

        if (applicationResponse.ok && applicationData.success) {
          // Auto-login after successful signup
          const loginResult = await login(formData.phone, formData.password);
          if (loginResult.success) {
            navigate('/fixer/dashboard');
          } else {
            setError('Account and application created successfully! Please log in.');
          }
        } else {
          setError(applicationData.detail || 'Account created but fixer application failed. Please contact support.');
        }
      } else {
        setError(userData.detail || 'Registration failed. Please try again.');
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-50 to-yellow-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <Logo 
            size="large" 
            variant="login" 
            showText={true}
            className="mb-8"
          />
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {currentStep === 1 ? 'Apply as Fixer' : currentStep === 2 ? 'Fixer Experience' : 'Secure Your Account'}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {currentStep === 1 
              ? 'Join our network of trusted service providers' 
              : currentStep === 2
              ? 'Tell us about your skills and experience'
              : 'Set a strong password to protect your account'
            }
          </p>
          
          {/* Progress Indicator */}
          <div className="mt-4 flex items-center justify-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${currentStep >= 1 ? 'bg-orange-600' : 'bg-gray-300'}`}></div>
            <div className="w-6 h-0.5 bg-gray-300"></div>
            <div className={`w-3 h-3 rounded-full ${currentStep >= 2 ? 'bg-orange-600' : 'bg-gray-300'}`}></div>
            <div className="w-6 h-0.5 bg-gray-300"></div>
            <div className={`w-3 h-3 rounded-full ${currentStep >= 3 ? 'bg-orange-600' : 'bg-gray-300'}`}></div>
          </div>
          <div className="text-center text-xs text-gray-500 mt-2">
            Step {currentStep} of 3
          </div>
        </div>

        {currentStep === 1 && (
          <form className="mt-8 space-y-6" onSubmit={(e) => { e.preventDefault(); handleNextStep(); }}>
            <div className="space-y-4">
              <div>
                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number *
                </label>
                <input
                  id="phone"
                  name="phone"
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={handleInputChange}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                  placeholder="e.g., +27821234567"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-2">
                    First Name *
                  </label>
                  <input
                    id="first_name"
                    name="first_name"
                    type="text"
                    required
                    value={formData.first_name}
                    onChange={handleInputChange}
                    className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                    placeholder="First name"
                  />
                </div>

                <div>
                  <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-2">
                    Last Name *
                  </label>
                  <input
                    id="last_name"
                    name="last_name"
                    type="text"
                    required
                    value={formData.last_name}
                    onChange={handleInputChange}
                    className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                    placeholder="Last name"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="id_number" className="block text-sm font-medium text-gray-700 mb-2">
                  South African ID Number *
                </label>
                <input
                  id="id_number"
                  name="id_number"
                  type="text"
                  required
                  maxLength="13"
                  value={formData.id_number}
                  onChange={handleInputChange}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                  placeholder="13-digit ID number"
                />
              </div>

              <div>
                <label htmlFor="town" className="block text-sm font-medium text-gray-700 mb-2">
                  Town/Local Municipality *
                </label>
                <input
                  id="town"
                  name="town"
                  type="text"
                  required
                  value={formData.town}
                  onChange={handleInputChange}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                  placeholder="e.g., Cape Town, Johannesburg, Durban"
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address (Optional)
                </label>
                <input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                  placeholder="your.email@example.com"
                />
              </div>
            </div>

            {error && (
              <div className="text-red-600 text-sm text-center bg-red-50 p-3 rounded-md">
                {error}
              </div>
            )}

            <div className="flex space-x-4">
              <Link
                to="/fixers-login"
                className="group relative w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
              >
                Back to Login
              </Link>
              <button
                type="submit"
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
              >
                Next: Experience →
              </button>
            </div>
          </form>
        )}

        {currentStep === 2 && (
          <form className="mt-8 space-y-6" onSubmit={(e) => { e.preventDefault(); handleNextStep(); }}>
            <div className="space-y-4">
              <div>
                <label htmlFor="services_offered" className="block text-sm font-medium text-gray-700 mb-2">
                  Services You Offer *
                </label>
                <textarea
                  id="services_offered"
                  name="services_offered"
                  required
                  rows={3}
                  value={formData.services_offered}
                  onChange={handleInputChange}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                  placeholder="e.g., Plumbing, Electrical work, Carpentry, etc."
                />
              </div>

              <div>
                <label htmlFor="experience_years" className="block text-sm font-medium text-gray-700 mb-2">
                  Years of Experience *
                </label>
                <select
                  id="experience_years"
                  name="experience_years"
                  required
                  value={formData.experience_years}
                  onChange={handleInputChange}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                >
                  <option value="">Select experience level</option>
                  <option value="0">Less than 1 year</option>
                  <option value="1">1-2 years</option>
                  <option value="3">3-5 years</option>
                  <option value="6">6-10 years</option>
                  <option value="11">More than 10 years</option>
                </select>
              </div>

              <div>
                <label htmlFor="qualifications" className="block text-sm font-medium text-gray-700 mb-2">
                  Qualifications & Certifications
                </label>
                <textarea
                  id="qualifications"
                  name="qualifications"
                  rows={3}
                  value={formData.qualifications}
                  onChange={handleInputChange}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                  placeholder="List your relevant qualifications, certifications, and training"
                />
              </div>

              <div>
                <label htmlFor="previous_work" className="block text-sm font-medium text-gray-700 mb-2">
                  Previous Work Experience
                </label>
                <textarea
                  id="previous_work"
                  name="previous_work"
                  rows={3}
                  value={formData.previous_work}
                  onChange={handleInputChange}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                  placeholder="Describe your previous work experience and notable projects"
                />
              </div>

              <div>
                <label htmlFor="why_fixer" className="block text-sm font-medium text-gray-700 mb-2">
                  Why do you want to be a fixer? *
                </label>
                <textarea
                  id="why_fixer"
                  name="why_fixer"
                  required
                  rows={3}
                  value={formData.why_fixer}
                  onChange={handleInputChange}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                  placeholder="Tell us about your motivation and what makes you a good fixer"
                />
              </div>

              {/* Document Uploads */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-gray-700">Document Verification (Optional but recommended)</h4>
                
                <div>
                  <label htmlFor="id_document" className="block text-xs text-gray-600 mb-1">
                    ID Document Copy
                  </label>
                  <input
                    id="id_document"
                    name="id_document"
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(e) => handleFileUpload('id_document', e.target.files[0])}
                    className="block w-full text-xs text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-xs file:font-medium file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
                  />
                </div>

                <div>
                  <label htmlFor="proof_of_address" className="block text-xs text-gray-600 mb-1">
                    Proof of Address
                  </label>
                  <input
                    id="proof_of_address"
                    name="proof_of_address"
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(e) => handleFileUpload('proof_of_address', e.target.files[0])}
                    className="block w-full text-xs text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-xs file:font-medium file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
                  />
                </div>

                <div>
                  <label htmlFor="qualifications_cert" className="block text-xs text-gray-600 mb-1">
                    Qualifications Certificate
                  </label>
                  <input
                    id="qualifications_cert"
                    name="qualifications_cert"
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(e) => handleFileUpload('qualifications_cert', e.target.files[0])}
                    className="block w-full text-xs text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-xs file:font-medium file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
                  />
                </div>

                <div>
                  <label htmlFor="criminal_clearance" className="block text-xs text-gray-600 mb-1">
                    Criminal Clearance Certificate
                  </label>
                  <input
                    id="criminal_clearance"
                    name="criminal_clearance"
                    type="file"
                    accept="image/*,.pdf"
                    onChange={(e) => handleFileUpload('criminal_clearance', e.target.files[0])}
                    className="block w-full text-xs text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-xs file:font-medium file:bg-orange-50 file:text-orange-700 hover:file:bg-orange-100"
                  />
                </div>
              </div>
            </div>

            {error && (
              <div className="text-red-600 text-sm text-center bg-red-50 p-3 rounded-md">
                {error}
              </div>
            )}

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={handlePreviousStep}
                className="group relative w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
              >
                ← Back
              </button>
              <button
                type="submit"
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
              >
                Next: Password →
              </button>
            </div>
          </form>
        )}

        {currentStep === 3 && (
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-orange-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-orange-800">
                      Fixer Application Summary
                    </h3>
                    <div className="mt-2 text-sm text-orange-700">
                      <p><strong>{formData.first_name} {formData.last_name}</strong></p>
                      <p>{formData.phone} • {formData.town}</p>
                      <p>Services: {formData.services_offered}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Password *
                </label>
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                  placeholder="Create a strong password"
                />
              </div>

              <div>
                <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700 mb-2">
                  Confirm Password *
                </label>
                <input
                  id="confirm_password"
                  name="confirm_password"
                  type="password"
                  required
                  value={formData.confirm_password}
                  onChange={handleInputChange}
                  className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
                  placeholder="Confirm your password"
                />
              </div>
            </div>

            {error && (
              <div className="text-red-600 text-sm text-center bg-red-50 p-3 rounded-md">
                {error}
              </div>
            )}

            <div className="flex space-x-4">
              <button
                type="button"
                onClick={handlePreviousStep}
                className="group relative w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
              >
                ← Back
              </button>
              <button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Submitting Application...</span>
                  </div>
                ) : (
                  'Submit Fixer Application'
                )}
              </button>
            </div>

            <div className="text-center text-xs text-gray-500">
              <p>
                Your fixer application will be reviewed by our team. 
                You'll be notified once approved to start accepting jobs.
              </p>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default FixerSignup;