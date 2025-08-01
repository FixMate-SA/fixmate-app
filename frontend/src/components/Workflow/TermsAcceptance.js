import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/api';
import { API_BASE_URL } from '../../utils/apiConfig';

const TermsAcceptance = ({ onAccept, showModal = false, onClose }) => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [hasAccepted, setHasAccepted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);
  const [showFullTerms, setShowFullTerms] = useState(false);

  useEffect(() => {
    checkTermsAcceptance();
  }, [user]);

  const checkTermsAcceptance = async () => {
    if (!user?.id) return;

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/terms/check/${user.id}`);
      const data = await response.json();
      setHasAccepted(data.has_accepted);
      
      if (data.has_accepted && onAccept) {
        onAccept(true);
      }
    } catch (error) {
      console.error('Error checking terms acceptance:', error);
    } finally {
      setLoading(false);
    }
  };

  const acceptTerms = async () => {
    if (!user?.id) return;

    setAccepting(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/terms/accept`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user.id,
          ip_address: window.location.hostname,
          user_agent: navigator.userAgent,
          method: 'web'
        })
      });

      if (response.ok) {
        setHasAccepted(true);
        if (onAccept) {
          onAccept(true);
        }
        if (onClose) {
          onClose();
        }
      } else {
        throw new Error('Failed to accept terms');
      }
    } catch (error) {
      console.error('Error accepting terms:', error);
      alert('Failed to accept terms. Please try again.');
    } finally {
      setAccepting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Checking terms acceptance...</span>
      </div>
    );
  }

  if (hasAccepted && !showModal) {
    return null;
  }

  const termsContent = `
FixMate-SA Platform Terms and Conditions

By using FixMate-SA, you agree to these terms:

1. SERVICE AGREEMENT
- FixMate-SA connects clients with independent service providers (fixers)
- All fixers are independent contractors, not employees of FixMate-SA
- Platform fee of R20 applies to each completed job

2. CLIENT OBLIGATIONS
- Accept terms before submitting service requests
- Provide accurate job descriptions and locations
- Allow fixer access to perform work as agreed
- Pay agreed amounts upon satisfactory completion

3. FIXER OBLIGATIONS
- Respond promptly to job notifications
- Complete accepted jobs or provide reasonable notice of cancellation
- Pay R20 platform fee for each completed job
- Maintain single job limit (one job at a time)

4. PAYMENT TERMS
- Platform fee of R20 per completed job
- Outstanding fees may restrict job assignment eligibility
- Admin may override restrictions in exceptional circumstances

5. QUALITY & MONITORING
- AI systems monitor fixer performance and behavior
- Persistent issues may result in account restrictions
- Fair job distribution algorithm ensures equitable opportunities

6. LIABILITY
- FixMate-SA facilitates connections but is not liable for work quality
- Disputes should be resolved directly between clients and fixers
- Emergency escalation available for urgent issues

7. TERMINATION
- Either party may terminate use at any time
- Outstanding fees remain payable after termination

By proceeding, you acknowledge understanding and acceptance of these terms.
  `;

  return (
    <div className={`${showModal ? 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50' : ''}`}>
      <div className={`bg-white rounded-lg ${showModal ? 'max-w-2xl max-h-full overflow-y-auto' : 'w-full'} p-6`}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center">
            ⚖️ {t('platformTerms', 'Platform Terms & Conditions')}
          </h2>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          )}
        </div>

        <div className="mb-6">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-yellow-800">
                  {t('termsRequired', 'Terms Acceptance Required')}
                </h3>
                <div className="mt-2 text-sm text-yellow-700">
                  <p>
                    {t('termsRequiredMessage', 'You must accept our platform terms and conditions before creating a service request. This ensures transparent operations and fair service delivery.')}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {showFullTerms ? (
            <div className="bg-gray-50 border rounded-lg p-4 max-h-64 overflow-y-auto">
              <pre className="text-sm text-gray-700 whitespace-pre-wrap">{termsContent}</pre>
            </div>
          ) : (
            <div className="bg-gray-50 border rounded-lg p-4">
              <p className="text-sm text-gray-700 mb-2">
                {t('termsPreview', 'Key highlights from our terms:')}
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• R20 platform fee per completed job</li>
                <li>• First come, first serve job assignment</li>
                <li>• AI monitoring for quality assurance</li>
                <li>• Fair distribution algorithm</li>
                <li>• Single job limit per fixer</li>
                <li>• Emergency escalation system</li>
              </ul>
            </div>
          )}

          <button
            onClick={() => setShowFullTerms(!showFullTerms)}
            className="mt-2 text-blue-600 hover:text-blue-800 text-sm underline"
          >
            {showFullTerms ? t('hideFullTerms', 'Hide Full Terms') : t('readFullTerms', 'Read Full Terms')}
          </button>
        </div>

        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <input
              type="checkbox"
              id="accept-terms"
              className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              onChange={(e) => setHasAccepted(e.target.checked)}
              disabled={accepting}
            />
            <label htmlFor="accept-terms" className="text-sm text-gray-700">
              {t('acceptTermsCheckbox', 'I have read, understood, and agree to the FixMate-SA Platform Terms and Conditions')}
            </label>
          </div>

          <div className="flex space-x-3">
            <button
              onClick={acceptTerms}
              disabled={!hasAccepted || accepting}
              className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors ${
                hasAccepted && !accepting
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
            >
              {accepting ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  {t('accepting', 'Accepting...')}
                </div>
              ) : (
                t('acceptAndContinue', 'Accept & Continue')
              )}
            </button>

            {onClose && (
              <button
                onClick={onClose}
                className="px-4 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                {t('cancel', 'Cancel')}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermsAcceptance;