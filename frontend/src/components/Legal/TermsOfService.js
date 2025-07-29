import React from 'react';
import { useNavigate } from 'react-router-dom';
import Logo from '../Common/Logo';

const TermsOfService = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <Logo size="medium" showText={true} />
            <button
              onClick={() => navigate('/')}
              className="text-indigo-600 hover:text-indigo-700 font-medium"
            >
              ← Back to FixMate-SA
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow-lg overflow-hidden sm:rounded-lg">
          <div className="px-8 py-10">
            <div className="prose prose-indigo max-w-none">
              <h1 className="text-4xl font-bold text-center mb-4 text-gray-900">
                Terms of Service for FixMate-SA
              </h1>
              <p className="text-sm text-center text-gray-500 mb-8 pb-6 border-b border-gray-200">
                Last Updated: July 1, 2025
              </p>

              <div className="space-y-6 text-gray-700 leading-relaxed">
                <p className="text-lg">
                  Welcome to FixMate-SA! These Terms of Service ("Terms") govern your use of the FixMate-SA platform, 
                  including our WhatsApp bot service and any associated websites or dashboards ("Platform"), operated by{' '}
                  <strong className="text-indigo-600">Donald Shai Technologies (Pty) Ltd</strong> ("we," "us," or "our").
                </p>
                <p className="text-lg">
                  By accessing or using our Platform, you agree to be bound by these Terms.
                </p>

                <div className="bg-indigo-50 border-l-4 border-indigo-400 p-6 my-8">
                  <h3 className="text-xl font-semibold text-indigo-800 mb-3">1. The FixMate-SA Service</h3>
                  <p className="text-indigo-700">
                    FixMate-SA is a technology platform that connects individuals seeking to obtain services ("Clients") 
                    with independent, third-party service providers ("Fixers").
                  </p>
                  <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
                    <p className="text-yellow-800 font-medium">
                      <strong>IMPORTANT:</strong> You acknowledge that FixMate-SA provides a platform to facilitate this connection. 
                      We are not an employer of Fixers. Fixers are independent contractors, and we are not responsible or liable 
                      for the actions, negligence, or work quality of any Fixer. Your contract for the service itself is between 
                      you (the Client) and the Fixer.
                    </p>
                  </div>
                </div>

                <div className="bg-gray-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">2. User Accounts</h3>
                  <div className="space-y-4">
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                        </svg>
                      </div>
                      <div>
                        <p><strong className="text-gray-800">Clients:</strong> A client account is automatically created when you interact with our WhatsApp service for the first time. You are responsible for all activity that occurs under your phone number.</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                        </svg>
                      </div>
                      <div>
                        <p><strong className="text-gray-800">Fixers:</strong> Fixers must be onboarded and are subject to a vetting process as outlined on the Platform.</p>
                      </div>
                    </div>
                    <div className="flex items-start space-x-3">
                      <div className="flex-shrink-0 w-6 h-6 bg-indigo-600 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                        </svg>
                      </div>
                      <div>
                        <p><strong className="text-gray-800">Administrators:</strong> An administrator ("Admin") is a user who has been granted special privileges by us to manage the platform.</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-blue-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-blue-800 mb-3">3. The Job Process</h3>
                  <p className="text-blue-700">
                    The job process includes a request, a quote for a call-out fee, payment for that fee, dispatch of a Fixer, 
                    acceptance by the Fixer, job completion, and a rating/feedback loop. The cost of the actual work performed 
                    beyond the call-out is negotiated directly between the Client and the Fixer.
                  </p>
                </div>

                <div className="bg-green-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-green-800 mb-4">4. Payments, Fees, and Refunds</h3>
                  <div className="space-y-3 text-green-700">
                    <div className="flex items-start space-x-3">
                      <span className="text-green-600 font-bold">•</span>
                      <p><strong>Client Call-Out Fee:</strong> All call-out fees are payable in advance through the Platform and are generally non-refundable once a Fixer has been dispatched.</p>
                    </div>
                    <div className="flex items-start space-x-3">
                      <span className="text-green-600 font-bold">•</span>
                      <p><strong>Fixer Service Fee:</strong> Fixers agree to pay a service fee to FixMate-SA for each completed job, as outlined in their Fixer Agreement.</p>
                    </div>
                  </div>
                </div>

                <div className="bg-red-50 border border-red-200 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-red-800 mb-3">5. Limitation of Liability</h3>
                  <p className="text-red-700">
                    To the fullest extent permitted by law, Donald Shai Technologies (Pty) Ltd shall not be liable for any 
                    indirect, incidental, special, consequential, or punitive damages resulting from your use of the Platform 
                    or the conduct or work of any Fixer or Client.
                  </p>
                </div>

                <div className="bg-gray-100 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">6. Governing Law</h3>
                  <p className="text-gray-700">
                    These Terms shall be governed by the laws of the Republic of South Africa.
                  </p>
                </div>

                <div className="bg-indigo-100 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-indigo-800 mb-3">7. Contact Us</h3>
                  <p className="text-indigo-700">
                    If you have any questions about these Terms, please contact us at:{' '}
                    <a href="mailto:legal@fixmatesa.org" className="font-bold text-indigo-600 hover:text-indigo-800 underline">
                      legal@fixmatesa.org
                    </a>
                  </p>
                </div>
              </div>

              {/* Company Information */}
              <div className="mt-12 pt-8 border-t border-gray-200 text-center bg-gray-50 -mx-8 -mb-10 px-8 py-8">
                <div className="space-y-2">
                  <p className="font-semibold text-gray-800 text-lg">
                    FixMate-SA is a product of Donald Shai Technologies (Pty) Ltd
                  </p>
                  <p className="text-sm text-gray-600">
                    Company Registration No: 2019/203656/07
                  </p>
                  <div className="flex justify-center items-center space-x-4 text-sm pt-4">
                    <button
                      onClick={() => navigate('/privacy')}
                      className="text-indigo-600 hover:text-indigo-800 font-medium"
                    >
                      Privacy Policy
                    </button>
                    <span className="text-gray-400">|</span>
                    <span className="text-gray-600">All rights reserved</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermsOfService;