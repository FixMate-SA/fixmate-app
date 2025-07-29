import React from 'react';
import { useNavigate } from 'react-router-dom';
import Logo from '../Common/Logo';

const PrivacyPolicy = () => {
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
                Privacy Policy for FixMate-SA
              </h1>
              <p className="text-sm text-center text-gray-500 mb-8 pb-6 border-b border-gray-200">
                Last Updated: July 1, 2025
              </p>

              <div className="space-y-6 text-gray-700 leading-relaxed">
                <p className="text-lg">
                  <strong className="text-indigo-600">Donald Shai Technologies (Pty) Ltd</strong> ("we," "us," or "our") 
                  is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, 
                  and safeguard your information when you use our FixMate-SA platform ("Platform"). This policy is drafted 
                  in accordance with the <strong className="text-indigo-600">Protection of Personal Information Act (POPIA)</strong> of South Africa.
                </p>

                <div className="bg-blue-50 border-l-4 border-blue-400 p-6">
                  <h3 className="text-xl font-semibold text-blue-800 mb-4">1. Information We Collect</h3>
                  <p className="text-blue-700 mb-4">
                    We collect personal information necessary to provide our service, including:
                  </p>
                  
                  <div className="space-y-4">
                    <div className="bg-white p-4 rounded-md border border-blue-200">
                      <h4 className="font-semibold text-blue-800 mb-2 flex items-center">
                        <svg className="w-5 h-5 mr-2 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd"></path>
                        </svg>
                        From Clients:
                      </h4>
                      <p className="text-blue-700 ml-7">
                        Contact details (WhatsApp number, name), job details (service descriptions, location), 
                        and feedback data (ratings, comments).
                      </p>
                    </div>
                    
                    <div className="bg-white p-4 rounded-md border border-blue-200">
                      <h4 className="font-semibold text-blue-800 mb-2 flex items-center">
                        <svg className="w-5 h-5 mr-2 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                        </svg>
                        From Fixers:
                      </h4>
                      <p className="text-blue-700 ml-7">
                        Identity and contact details, skills, vetting information, and real-time location data 
                        during an active job.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-green-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-green-800 mb-3">
                    2. How We Use Your Information (Purpose of Processing)
                  </h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-white p-4 rounded-md border border-green-200">
                      <div className="flex items-center mb-2">
                        <svg className="w-5 h-5 mr-2 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12A3 3 0 017 13s.879.5 2.5.5c0-1 .5-4 1.25-4.5.5 1 .786 1.293 1.371 1.879A2.99 2.99 0 0113 13a2.99 2.99 0 01-.879 2.121z" clipRule="evenodd"></path>
                        </svg>
                        <h4 className="font-semibold text-green-800">Service Connection</h4>
                      </div>
                      <p className="text-green-700 text-sm">Connect Clients with Fixers efficiently</p>
                    </div>
                    
                    <div className="bg-white p-4 rounded-md border border-green-200">
                      <div className="flex items-center mb-2">
                        <svg className="w-5 h-5 mr-2 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M4 4a2 2 0 00-2 2v1h16V6a2 2 0 00-2-2H4z"></path>
                          <path fillRule="evenodd" d="M18 9H2v5a2 2 0 002 2h12a2 2 0 002-2V9zM4 13a1 1 0 011-1h1a1 1 0 110 2H5a1 1 0 01-1-1zm5-1a1 1 0 100 2h1a1 1 0 100-2H9z" clipRule="evenodd"></path>
                        </svg>
                        <h4 className="font-semibold text-green-800">Payment Processing</h4>
                      </div>
                      <p className="text-green-700 text-sm">Process payments securely and transparently</p>
                    </div>
                    
                    <div className="bg-white p-4 rounded-md border border-green-200">
                      <div className="flex items-center mb-2">
                        <svg className="w-5 h-5 mr-2 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path>
                        </svg>
                        <h4 className="font-semibold text-green-800">Safety & Quality</h4>
                      </div>
                      <p className="text-green-700 text-sm">Maintain safety and quality standards</p>
                    </div>
                    
                    <div className="bg-white p-4 rounded-md border border-green-200">
                      <div className="flex items-center mb-2">
                        <svg className="w-5 h-5 mr-2 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd"></path>
                        </svg>
                        <h4 className="font-semibold text-green-800">Communication</h4>
                      </div>
                      <p className="text-green-700 text-sm">Communicate about service requests and updates</p>
                    </div>
                  </div>
                </div>

                <div className="bg-orange-50 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-orange-800 mb-3">3. Data Sharing and Disclosure</h3>
                  <div className="space-y-3 text-orange-700">
                    <p>We only share information when necessary to provide the service:</p>
                    <div className="grid md:grid-cols-2 gap-4 mt-4">
                      <div className="bg-white p-4 rounded-md border border-orange-200">
                        <p className="text-sm"><strong>Client to Fixer:</strong> Job details and contact info are shared with the assigned Fixer.</p>
                      </div>
                      <div className="bg-white p-4 rounded-md border border-orange-200">
                        <p className="text-sm"><strong>Fixer to Client:</strong> Fixer's name is shared with the Client.</p>
                      </div>
                    </div>
                    <div className="mt-4 p-4 bg-orange-100 border border-orange-300 rounded-md">
                      <p className="text-orange-800 font-medium">
                        <strong>Important:</strong> We do not sell your personal information.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="bg-purple-50 border border-purple-200 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-purple-800 mb-4 flex items-center">
                    <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 8a6 6 0 01-7.743 5.743L10 14l-1 1-1 1H6v2H2v-4l4.257-4.257A6 6 0 1118 8zm-6-4a1 1 0 100 2 2 2 0 012 2 1 1 0 102 0 4 4 0 00-4-4z" clipRule="evenodd"></path>
                    </svg>
                    4. Your Rights Under POPIA
                  </h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-3">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center">
                          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                          </svg>
                        </div>
                        <p className="text-purple-700 text-sm">Access your personal information</p>
                      </div>
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center">
                          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                          </svg>
                        </div>
                        <p className="text-purple-700 text-sm">Correct inaccurate information</p>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center">
                          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                          </svg>
                        </div>
                        <p className="text-purple-700 text-sm">Delete your personal information</p>
                      </div>
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 w-6 h-6 bg-purple-600 rounded-full flex items-center justify-center">
                          <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path>
                          </svg>
                        </div>
                        <p className="text-purple-700 text-sm">Object to processing</p>
                      </div>
                    </div>
                  </div>
                  <p className="text-purple-700 mt-4">
                    To exercise these rights, please contact our Information Officer.
                  </p>
                </div>

                <div className="bg-indigo-100 p-6 rounded-lg">
                  <h3 className="text-xl font-semibold text-indigo-800 mb-4 flex items-center">
                    <svg className="w-6 h-6 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"></path>
                    </svg>
                    5. Contact Us
                  </h3>
                  <div className="bg-white p-4 rounded-md border border-indigo-200">
                    <p className="text-indigo-700 mb-3">
                      If you have any questions or concerns, please contact our designated Information Officer:
                    </p>
                    <div className="space-y-2">
                      <div className="flex items-center space-x-2">
                        <svg className="w-4 h-4 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd"></path>
                        </svg>
                        <span className="text-indigo-800 font-medium">Name:</span>
                        <span className="text-indigo-700">Donald Shai</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <svg className="w-4 h-4 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"></path>
                          <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"></path>
                        </svg>
                        <span className="text-indigo-800 font-medium">Email:</span>
                        <a href="mailto:popia@fixmatesa.org" className="text-indigo-600 hover:text-indigo-800 underline font-medium">
                          popia@fixmatesa.org
                        </a>
                      </div>
                    </div>
                  </div>
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
                      onClick={() => navigate('/terms')}
                      className="text-indigo-600 hover:text-indigo-800 font-medium"
                    >
                      Terms of Service
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

export default PrivacyPolicy;