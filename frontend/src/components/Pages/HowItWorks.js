import React from 'react';

const HowItWorks = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">How FixMate-SA Works</h1>
          <p className="text-xl text-gray-600">Getting your home fixed has never been easier</p>
        </header>

        {/* For Customers */}
        <section className="mb-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">For Customers</h2>
            <p className="text-lg text-gray-600">Get your home repairs done by trusted professionals in just a few simple steps</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">1. Create Your Request</h3>
              <p className="text-gray-600">Describe your repair needs, upload photos, and set your location. Our AI will help categorize your job.</p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">2. Smart Matching</h3>
              <p className="text-gray-600">Our AI finds the best fixers near you based on skills, ratings, availability, and fair distribution.</p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-10 h-10 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">3. Connect & Confirm</h3>
              <p className="text-gray-600">Qualified fixers accept your job first-come-first-served. You get their details and can track progress.</p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-10 h-10 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold mb-2">4. Job Complete & Rate</h3>
              <p className="text-gray-600">After completion with photo verification, rate your fixer. The R20 platform fee is automatically handled.</p>
            </div>
          </div>
        </section>

        {/* Key Features */}
        <section className="bg-white rounded-lg shadow-lg p-8 mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Smart Features That Protect You</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">🔒 Terms Acceptance</h3>
              <p className="text-gray-600">All jobs require terms acceptance before submission for legal protection.</p>
            </div>
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">⏰ 180-Minute Guarantee</h3>
              <p className="text-gray-600">If your fixer doesn't arrive within 3 hours, we automatically reassign your job.</p>
            </div>
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">📸 Photo Verification</h3>
              <p className="text-gray-600">Before and after photos ensure quality work completion.</p>
            </div>
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">🤖 AI Fraud Detection</h3>
              <p className="text-gray-600">Our AI monitors patterns to detect and prevent fraudulent activity.</p>
            </div>
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">⚖️ Dispute Resolution</h3>
              <p className="text-gray-600">Professional mediation for any service disputes with payment protection.</p>
            </div>
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold text-gray-900 mb-2">🆘 Emergency Escalation</h3>
              <p className="text-gray-600">Urgent issues get immediate admin attention and priority handling.</p>
            </div>
          </div>
        </section>

        {/* Multiple Ways to Access */}
        <section className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8 mb-16">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold mb-4">Access FixMate-SA Your Way</h2>
            <p className="text-lg">Choose the method that works best for you</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-white bg-opacity-10 rounded-lg">
              <div className="text-4xl mb-4">📱</div>
              <h3 className="text-xl font-semibold mb-2">Smartphone App</h3>
              <p>Full-featured mobile app with all advanced features, photo uploads, and real-time tracking.</p>
            </div>
            <div className="text-center p-6 bg-white bg-opacity-10 rounded-lg">
              <div className="text-4xl mb-4">💬</div>
              <h3 className="text-xl font-semibold mb-2">SMS/MMS</h3>
              <p>Text-based service for feature phones. Send job requests, receive updates, and manage jobs via SMS.</p>
            </div>
            <div className="text-center p-6 bg-white bg-opacity-10 rounded-lg">
              <div className="text-4xl mb-4">☎️</div>
              <h3 className="text-xl font-semibold mb-2">USSD</h3>
              <p>Dial our USSD code for interactive menu-based access to core features on any mobile phone.</p>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="text-center bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Ready to Get Started?</h2>
          <p className="text-lg text-gray-600 mb-8">Join thousands of satisfied customers and professional fixers across South Africa</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => window.location.href = '/signup'} 
              className="bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-blue-700 transition text-lg"
            >
              Find a Fixer Now
            </button>
            <button 
              onClick={() => window.location.href = '/become-fixer'} 
              className="bg-green-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-green-700 transition text-lg"
            >
              Start Earning as a Fixer
            </button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default HowItWorks;