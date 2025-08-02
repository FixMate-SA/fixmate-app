import React from 'react';

const BecomeFixer = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4">
        {/* Hero Section */}
        <section className="bg-gradient-to-r from-blue-600 to-green-600 text-white rounded-lg p-12 mb-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Become a FixMate-SA Fixer</h1>
          <p className="text-xl md:text-2xl mb-8">Turn your skills into steady income with South Africa's premier service platform</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <div className="text-3xl font-bold mb-2">R2,500+</div>
              <div className="text-green-100">Average Monthly Earnings</div>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <div className="text-3xl font-bold mb-2">50+</div>
              <div className="text-green-100">Jobs Per Month</div>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <div className="text-3xl font-bold mb-2">4.8/5</div>
              <div className="text-green-100">Fixer Satisfaction</div>
            </div>
          </div>
        </section>

        {/* Why Join Us */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Why Choose FixMate-SA?</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2-1.343-2-3-2z"></path>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v8m0 0V9m0 7c1.11 0 2.08-.402 2.599-1M12 16c-1.657 0-3-.895-3-2s1.343-2 3-2"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Steady Income Stream</h3>
              <p className="text-gray-600">Our AI-powered matching system ensures consistent job flow based on your skills and availability.</p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Smart Job Matching</h3>
              <p className="text-gray-600">Get matched with jobs that fit your expertise, location, and schedule perfectly.</p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Trust & Safety</h3>
              <p className="text-gray-600">Comprehensive background checks and safety features protect both you and your customers.</p>
            </div>
          </div>
        </section>

        {/* Services We Need */}
        <section className="bg-white rounded-lg shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">Services We Need</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <div className="text-center p-4 border rounded-lg hover:bg-gray-50">
              <div className="text-3xl mb-2">🔧</div>
              <div className="font-semibold">Plumbing</div>
            </div>
            <div className="text-center p-4 border rounded-lg hover:bg-gray-50">
              <div className="text-3xl mb-2">⚡</div>
              <div className="font-semibold">Electrical</div>
            </div>
            <div className="text-center p-4 border rounded-lg hover:bg-gray-50">
              <div className="text-3xl mb-2">🎨</div>
              <div className="font-semibold">Painting</div>
            </div>
            <div className="text-center p-4 border rounded-lg hover:bg-gray-50">
              <div className="text-3xl mb-2">🏠</div>
              <div className="font-semibold">Carpentry</div>
            </div>
            <div className="text-center p-4 border rounded-lg hover:bg-gray-50">
              <div className="text-3xl mb-2">❄️</div>
              <div className="font-semibold">HVAC</div>
            </div>
            <div className="text-center p-4 border rounded-lg hover:bg-gray-50">
              <div className="text-3xl mb-2">🔒</div>
              <div className="font-semibold">Locksmith</div>
            </div>
            <div className="text-center p-4 border rounded-lg hover:bg-gray-50">
              <div className="text-3xl mb-2">🏗️</div>
              <div className="font-semibold">General Repairs</div>
            </div>
            <div className="text-center p-4 border rounded-lg hover:bg-gray-50">
              <div className="text-3xl mb-2">🧹</div>
              <div className="font-semibold">Cleaning</div>
            </div>
          </div>
        </section>

        {/* Application Process */}
        <section className="bg-white rounded-lg shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">Simple 4-Step Application Process</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-blue-600">1</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Apply Online</h3>
              <p className="text-gray-600">Fill out our simple application form with your details and skills.</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-green-600">2</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Verification</h3>
              <p className="text-gray-600">We verify your identity, background, and qualifications.</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-purple-600">3</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Skills Test</h3>
              <p className="text-gray-600">Complete a practical skills assessment in your chosen area.</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-bold text-yellow-600">4</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Get Approved</h3>
              <p className="text-gray-600">Once approved, start receiving job matches immediately!</p>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-12 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Your Success Story?</h2>
          <p className="text-xl mb-8">Join thousands of successful fixers already earning with FixMate-SA</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => window.location.href = '/signup'} 
              className="bg-white text-blue-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-gray-100 transition"
            >
              Apply Now - It's Free!
            </button>
            <button 
              onClick={() => window.location.href = '/help-center'} 
              className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-white hover:text-blue-600 transition"
            >
              Have Questions?
            </button>
          </div>
          <p className="text-sm text-blue-100 mt-4">Application takes less than 10 minutes. Start earning within 48 hours of approval!</p>
        </section>
      </div>
    </div>
  );
};

export default BecomeFixer;