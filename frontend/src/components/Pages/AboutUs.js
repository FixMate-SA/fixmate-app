import React from 'react';

const AboutUs = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">About FixMate-SA</h1>
          <p className="text-xl text-gray-600">Connecting South Africans with trusted home repair professionals</p>
        </header>

        <section className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Our Story</h2>
          <p className="text-gray-700 mb-4">
            FixMate-SA was born from a simple yet powerful vision: to transform how South Africans access reliable home repair and maintenance services. Founded with the understanding that finding trustworthy fixers shouldn't be a challenge, we've built a comprehensive platform that bridges the gap between skilled professionals and homeowners across South Africa.
          </p>
          <p className="text-gray-700 mb-4">
            Our platform combines cutting-edge technology with deep local knowledge, ensuring that whether you're in Cape Town, Johannesburg, Durban, or any corner of Mzansi, quality service is just a few taps away.
          </p>
        </section>

        <section className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">What Makes Us Different</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">1</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">AI-Powered Smart Matching</h3>
                <p className="text-gray-600">Our advanced AI system matches you with the perfect fixer based on location, skills, availability, and past performance.</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">2</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Inclusive Technology</h3>
                <p className="text-gray-600">Supporting both smartphone and feature phone users through SMS/MMS and USSD integration.</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">3</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Trust & Safety First</h3>
                <p className="text-gray-600">Photo verification, dispute resolution, and AI-powered fraud prevention keep you safe.</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 w-8 h-8 bg-red-500 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">4</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Local Expertise</h3>
                <p className="text-gray-600">Multi-language support and deep understanding of South African communities and needs.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Our Impact</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div className="p-4">
              <div className="text-3xl font-bold text-blue-600 mb-2">10,000+</div>
              <div className="text-gray-600">Jobs Completed</div>
            </div>
            <div className="p-4">
              <div className="text-3xl font-bold text-green-600 mb-2">2,500+</div>
              <div className="text-gray-600">Verified Fixers</div>
            </div>
            <div className="p-4">
              <div className="text-3xl font-bold text-purple-600 mb-2">98%</div>
              <div className="text-gray-600">Customer Satisfaction</div>
            </div>
          </div>
        </section>

        <section className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">Our Mission</h2>
          <p className="text-gray-700 mb-4">
            To democratize access to quality home repair services across South Africa by creating a trusted, technology-driven platform that empowers both service providers and customers.
          </p>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Our Values</h3>
          <ul className="list-disc list-inside text-gray-700 space-y-2">
            <li><strong>Ubuntu:</strong> We believe in the interconnectedness of our community</li>
            <li><strong>Excellence:</strong> We strive for the highest quality in everything we do</li>
            <li><strong>Innovation:</strong> We embrace technology to solve real problems</li>
            <li><strong>Trust:</strong> We build lasting relationships through transparency and reliability</li>
            <li><strong>Empowerment:</strong> We create opportunities for economic growth and skills development</li>
          </ul>
        </section>

        <section className="bg-blue-600 text-white rounded-lg p-8 text-center">
          <h2 className="text-2xl font-semibold mb-4">Join the FixMate-SA Family</h2>
          <p className="mb-6">Whether you're looking for reliable home repairs or want to grow your fixing business, we're here to help.</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => window.location.href = '/signup'} 
              className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
            >
              Find a Fixer
            </button>
            <button 
              onClick={() => window.location.href = '/become-fixer'} 
              className="bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-800 transition border-2 border-white"
            >
              Become a Fixer
            </button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default AboutUs;