import React from 'react';
import BackButton from '../Common/BackButton';

const SafetyTrust = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4">
        {/* Back Navigation */}
        <div className="mb-8">
          <BackButton text="← Back" />
        </div>

        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Safety & Trust</h1>
          <p className="text-xl text-gray-600">Your security is our top priority - built into every feature</p>
        </header>

        {/* Trust Score */}
        <section className="bg-gradient-to-r from-green-500 to-blue-600 text-white rounded-lg p-8 mb-12 text-center">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
              <div className="text-3xl font-bold mb-2">98%</div>
              <div className="text-green-100">Customer Satisfaction</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">99.8%</div>
              <div className="text-green-100">Fraud-Free Transactions</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">24/7</div>
              <div className="text-green-100">Safety Monitoring</div>
            </div>
            <div>
              <div className="text-3xl font-bold mb-2">2,500+</div>
              <div className="text-green-100">Verified Fixers</div>
            </div>
          </div>
        </section>

        {/* Core Safety Features */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Multi-Layer Security System</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Fixer Verification</h3>
              <p className="text-gray-600 mb-4">Every fixer undergoes thorough identity verification, skills assessment, and background checks before joining our platform.</p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• ID document verification</li>
                <li>• Skills certification</li>
                <li>• Reference checks</li>
                <li>• Criminal background screening</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">AI Fraud Detection</h3>
              <p className="text-gray-600 mb-4">Our advanced AI monitors patterns and behaviors to detect and prevent fraudulent activity in real-time.</p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Pattern recognition analysis</li>
                <li>• Behavioral anomaly detection</li>
                <li>• Risk scoring (0-100 scale)</li>
                <li>• Automatic alerts and intervention</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Photo Verification</h3>
              <p className="text-gray-600 mb-4">Before and after photos ensure quality work completion and provide evidence for any disputes.</p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Mandatory before photos</li>
                <li>• Progress documentation</li>
                <li>• Completion verification</li>
                <li>• AI quality assessment</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Emergency Protocols</h3>
              <p className="text-gray-600 mb-4">Comprehensive emergency response system for immediate assistance when things go wrong.</p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Panic button in-app</li>
                <li>• 180-minute response guarantee</li>
                <li>• Auto-escalation system</li>
                <li>• Emergency admin intervention</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Secure Payments</h3>
              <p className="text-gray-600 mb-4">Protected payment processing with escrow services and fraud protection measures.</p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Payment escrow protection</li>
                <li>• R20 platform fee system</li>
                <li>• 48-hour payment deadline</li>
                <li>• Dispute-protected transactions</li>
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Dispute Resolution</h3>
              <p className="text-gray-600 mb-4">Professional mediation service to resolve conflicts fairly with payment protection.</p>
              <ul className="text-sm text-gray-500 space-y-1">
                <li>• Professional mediation</li>
                <li>• Multiple dispute categories</li>
                <li>• Evidence-based resolution</li>
                <li>• Payment hold protection</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Emergency Support */}
        <section className="bg-red-50 border border-red-200 rounded-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-red-900 mb-4">🚨 Emergency Response</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl mb-2">🚨</div>
              <h3 className="font-semibold text-red-900 mb-2">Immediate Issues</h3>
              <p className="text-red-700">Use the panic button for safety emergencies. Admin responds within minutes.</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">📞</div>
              <h3 className="font-semibold text-red-900 mb-2">24/7 Support</h3>
              <p className="text-red-700">Our support team monitors all jobs and responds to incidents around the clock.</p>
            </div>
            <div className="text-center">
              <div className="text-3xl mb-2">⚡</div>
              <h3 className="font-semibold text-red-900 mb-2">Auto-Escalation</h3>
              <p className="text-red-700">System automatically escalates late arrivals and unresponsive fixers.</p>
            </div>
          </div>
        </section>

        {/* Contact Safety */}
        <section className="bg-gray-900 text-white rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold mb-4">Need Help or Have Safety Concerns?</h2>
          <p className="text-gray-300 mb-6">Our safety team is here to help 24/7</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => window.location.href = '/help-center'} 
              className="bg-red-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-red-700 transition"
            >
              Emergency Support
            </button>
            <button 
              onClick={() => window.location.href = '/help-center'} 
              className="bg-white text-gray-900 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
            >
              Help Center
            </button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default SafetyTrust;