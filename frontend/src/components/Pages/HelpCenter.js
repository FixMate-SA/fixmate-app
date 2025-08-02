import React, { useState } from 'react';

const HelpCenter = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSearch = (e) => {
    setSearchTerm(e.target.value.toLowerCase());
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Help Center</h1>
          <p className="text-xl text-gray-600">Find answers to your questions and get the support you need</p>
          
          {/* Search Bar */}
          <div className="max-w-md mx-auto mt-8">
            <div className="relative">
              <input 
                type="text" 
                placeholder="Search for help..." 
                className="w-full px-4 py-3 pr-12 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                onChange={handleSearch}
              />
              <button className="absolute right-3 top-3 text-gray-400 hover:text-gray-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
              </button>
            </div>
          </div>
        </header>

        {/* Quick Actions */}
        <section className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
          <div className="bg-blue-500 text-white p-6 rounded-lg text-center hover:bg-blue-600 transition cursor-pointer">
            <div className="text-3xl mb-2">👤</div>
            <h3 className="font-semibold mb-2">Customer Help</h3>
            <p className="text-sm text-blue-100">Find fixers, manage jobs, payments</p>
          </div>
          <div className="bg-green-500 text-white p-6 rounded-lg text-center hover:bg-green-600 transition cursor-pointer">
            <div className="text-3xl mb-2">🔧</div>
            <h3 className="font-semibold mb-2">Fixer Help</h3>
            <p className="text-sm text-green-100">Job matching, earnings, profiles</p>
          </div>
          <div className="bg-red-500 text-white p-6 rounded-lg text-center hover:bg-red-600 transition cursor-pointer">
            <div className="text-3xl mb-2">🚨</div>
            <h3 className="font-semibold mb-2">Emergency</h3>
            <p className="text-sm text-red-100">Urgent issues, safety concerns</p>
          </div>
          <div className="bg-purple-500 text-white p-6 rounded-lg text-center hover:bg-purple-600 transition cursor-pointer">
            <div className="text-3xl mb-2">💬</div>
            <h3 className="font-semibold mb-2">Contact Us</h3>
            <p className="text-sm text-purple-100">Chat, email, phone support</p>
          </div>
        </section>

        {/* Customer FAQ */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Customer Support</h2>
          <div className="space-y-4">
            <details className="bg-white rounded-lg shadow p-6">
              <summary className="cursor-pointer font-semibold text-gray-900 mb-4">How do I create a job request?</summary>
              <div className="text-gray-600 space-y-2">
                <p>Creating a job request is simple:</p>
                <ol className="list-decimal list-inside space-y-1 ml-4">
                  <li>Click "Create New Job" on your dashboard</li>
                  <li>Describe your repair needs in detail</li>
                  <li>Upload photos if possible (helps fixers understand the job)</li>
                  <li>Set your location and preferred timing</li>
                  <li>Accept our terms and conditions</li>
                  <li>Submit your request</li>
                </ol>
                <p className="mt-2">Our AI will automatically match you with qualified fixers in your area!</p>
              </div>
            </details>

            <details className="bg-white rounded-lg shadow p-6">
              <summary className="cursor-pointer font-semibold text-gray-900 mb-4">How does the smart matching system work?</summary>
              <div className="text-gray-600">
                <p>Our AI-powered matching considers multiple factors:</p>
                <ul className="list-disc list-inside mt-2 space-y-1 ml-4">
                  <li><strong>Proximity:</strong> Fixers closest to your location</li>
                  <li><strong>Skills Match:</strong> Fixers with relevant expertise</li>
                  <li><strong>Availability:</strong> Fixers currently available for work</li>
                  <li><strong>Rating:</strong> Highly-rated fixers (≥3.0 stars or new fixers)</li>
                  <li><strong>Payment Status:</strong> Fixers with no outstanding fees</li>
                  <li><strong>Fair Distribution:</strong> Ensures equal opportunities for all fixers</li>
                </ul>
                <p className="mt-2">Qualified fixers receive notifications and can accept your job first-come-first-served.</p>
              </div>
            </details>

            <details className="bg-white rounded-lg shadow p-6">
              <summary className="cursor-pointer font-semibold text-gray-900 mb-4">What happens if my fixer doesn't show up?</summary>
              <div className="text-gray-600">
                <p>We have a comprehensive timeout system:</p>
                <ul className="list-disc list-inside mt-2 space-y-1 ml-4">
                  <li><strong>180-Minute Window:</strong> Fixers have 3 hours to arrive after accepting</li>
                  <li><strong>Auto-Escalation:</strong> If they don't arrive, your job is flagged as "EMERGENCY"</li>
                  <li><strong>Automatic Reassignment:</strong> We immediately reassign your job to other qualified fixers</li>
                  <li><strong>Fixer Penalty:</strong> The original fixer gets marked "unavailable" for 4 hours</li>
                  <li><strong>No Cost to You:</strong> You don't pay anything if a fixer doesn't show up</li>
                </ul>
                <p className="mt-2">Our system ensures you get reliable service or we find you someone who will!</p>
              </div>
            </details>
          </div>
        </section>

        {/* Emergency Support */}
        <section className="bg-red-50 border border-red-200 rounded-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-red-900 mb-4">🚨 Emergency Support</h2>
          <p className="text-red-700 mb-6">For immediate safety concerns or urgent issues, use these resources:</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-4 rounded-lg">
              <h3 className="font-semibold text-red-900 mb-2">In-App Emergency</h3>
              <p className="text-red-700 mb-3">Use the panic button in the app for immediate admin response.</p>
              <span className="inline-block bg-red-500 text-white px-3 py-1 rounded text-sm">Response: 2-5 minutes</span>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <h3 className="font-semibold text-red-900 mb-2">WhatsApp Emergency</h3>
              <p className="text-red-700 mb-3">Send "EMERGENCY" to our WhatsApp line for urgent help.</p>
              <span className="inline-block bg-red-500 text-white px-3 py-1 rounded text-sm">+27 XX XXX XXXX</span>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <h3 className="font-semibold text-red-900 mb-2">SMS Emergency</h3>
              <p className="text-red-700 mb-3">Text "HELP" with your location for immediate assistance.</p>
              <span className="inline-block bg-red-500 text-white px-3 py-1 rounded text-sm">SMS: 12345</span>
            </div>
          </div>
        </section>

        {/* Contact Section */}
        <section className="mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Contact Support</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Live Chat</h3>
              <p className="text-gray-600 mb-4">Chat with our support team in real-time</p>
              <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition">Start Chat</button>
              <div className="text-sm text-gray-500 mt-2">Available 24/7</div>
            </div>

            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Email</h3>
              <p className="text-gray-600 mb-4">Send us a detailed message</p>
              <a href="mailto:support@fixmate-sa.com" className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition inline-block">Send Email</a>
              <div className="text-sm text-gray-500 mt-2">Response: 2-4 hours</div>
            </div>

            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Phone</h3>
              <p className="text-gray-600 mb-4">Speak directly with support</p>
              <a href="tel:+27123456789" className="bg-purple-500 text-white px-4 py-2 rounded hover:bg-purple-600 transition inline-block">Call Now</a>
              <div className="text-sm text-gray-500 mt-2">Mo-Su 6AM-10PM</div>
            </div>

            <div className="bg-white rounded-lg shadow p-6 text-center">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"></path>
                </svg>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">WhatsApp</h3>
              <p className="text-gray-600 mb-4">Message us on WhatsApp</p>
              <a href="https://wa.me/27123456789" className="bg-yellow-500 text-white px-4 py-2 rounded hover:bg-yellow-600 transition inline-block">Message</a>
              <div className="text-sm text-gray-500 mt-2">Quick responses</div>
            </div>
          </div>
        </section>

        {/* Community */}
        <section className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg p-8 text-center">
          <h2 className="text-2xl font-bold mb-4">Join Our Community</h2>
          <p className="text-lg mb-6">Connect with other FixMate-SA users, share tips, and get community support</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition">Facebook Group</button>
            <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition">Telegram Channel</button>
            <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition">WhatsApp Community</button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default HelpCenter;