import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-12">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Company Info */}
          <div className="md:pr-8">
            <div className="flex items-center mb-6">
              <img src="/fixmate-logo.jpg" alt="FixMate-SA" className="h-12 w-12 rounded-lg mr-3" />
              <h3 className="text-2xl font-bold">FixMate-SA</h3>
            </div>
            <p className="text-gray-300 mb-6 leading-relaxed">
              South Africa's premier service marketplace connecting skilled fixers with clients across all 11 official languages. Professional, reliable, and trusted by thousands.
            </p>
            <div className="flex items-center space-x-6 text-sm">
              <div className="flex items-center">
                <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                <span className="text-gray-400">Proudly South African</span>
              </div>
              <div className="flex items-center">
                <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                <span className="text-gray-400">11 Languages</span>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div className="md:px-4">
            <h4 className="text-xl font-semibold mb-6 text-center">Quick Links</h4>
            <ul className="space-y-4 text-center">
              <li>
                <Link to="/about-us" className="text-gray-300 hover:text-white transition-colors duration-200 text-lg">
                  About Us
                </Link>
              </li>
              <li>
                <Link to="/how-it-works" className="text-gray-300 hover:text-white transition-colors duration-200 text-lg">
                  How It Works
                </Link>
              </li>
              <li>
                <Link to="/safety-trust" className="text-gray-300 hover:text-white transition-colors duration-200 text-lg">
                  Safety & Trust
                </Link>
              </li>
              <li>
                <Link to="/become-fixer" className="text-gray-300 hover:text-white transition-colors duration-200 text-lg">
                  Become a Fixer
                </Link>
              </li>
              <li>
                <Link to="/help-center" className="text-gray-300 hover:text-white transition-colors duration-200 text-lg">
                  Help Center
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div className="md:pl-4">
            <h4 className="text-xl font-semibold mb-6 text-center">Support</h4>
            <ul className="space-y-4">
              <li className="flex items-center justify-center md:justify-start text-gray-300">
                <svg className="w-5 h-5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                </svg>
                <span className="text-lg">+27 (0) 11 123 4567</span>
              </li>
              <li className="flex items-center justify-center md:justify-start text-gray-300">
                <svg className="w-5 h-5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
                <span className="text-lg">support@fixmate-sa.com</span>
              </li>
              <li className="flex items-center justify-center md:justify-start text-gray-300">
                <svg className="w-5 h-5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
                <span className="text-lg">SMS: 32123 (FixMate)</span>
              </li>
              <li className="flex items-center justify-center md:justify-start text-gray-300">
                <svg className="w-5 h-5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                <span className="text-lg text-center md:text-left">Cape Town, Johannesburg, Durban</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-gray-700 mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-center md:text-left">
              <p className="text-gray-400 text-base mb-1">
                FixMate-SA is a product of Donald Shai Technologies (Pty) Ltd. All rights reserved.
              </p>
              <p className="text-gray-500 text-sm">
                Company Registration No: 2019/288556/07
              </p>
            </div>
            
            <div className="flex space-x-8">
              <Link to="/terms-of-service" className="text-gray-400 hover:text-white text-base transition-colors duration-200">
                Terms of Service
              </Link>
              <Link to="/privacy-policy" className="text-gray-400 hover:text-white text-base transition-colors duration-200">
                Privacy Policy
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;