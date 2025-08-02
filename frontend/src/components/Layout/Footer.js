import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-12">
      <div className="max-w-6xl mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center mb-4">
              <img src="/fixmate-logo.jpg" alt="FixMate-SA" className="h-12 w-12 rounded-lg mr-3" />
              <h3 className="text-xl font-bold">FixMate-SA</h3>
            </div>
            <p className="text-gray-300 mb-4">
              South Africa's premier service marketplace connecting skilled fixers with clients across all 11 official languages. Professional, reliable, and trusted by thousands.
            </p>
            <div className="flex items-center space-x-4 text-sm text-gray-400">
              <div className="flex items-center">
                <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                Proudly South African
              </div>
              <div className="flex items-center">
                <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                11 Languages
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/about-us" className="text-gray-300 hover:text-white transition">
                  About Us
                </Link>
              </li>
              <li>
                <Link to="/how-it-works" className="text-gray-300 hover:text-white transition">
                  How It Works
                </Link>
              </li>
              <li>
                <Link to="/safety-trust" className="text-gray-300 hover:text-white transition">
                  Safety & Trust
                </Link>
              </li>
              <li>
                <Link to="/become-fixer" className="text-gray-300 hover:text-white transition">
                  Become a Fixer
                </Link>
              </li>
              <li>
                <Link to="/help-center" className="text-gray-300 hover:text-white transition">
                  Help Center
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Support</h4>
            <ul className="space-y-2">
              <li className="flex items-center text-gray-300">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                </svg>
                +27 (0) 11 123 4567
              </li>
              <li className="flex items-center text-gray-300">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
                support@fixmate-sa.com
              </li>
              <li className="flex items-center text-gray-300">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"></path>
                </svg>
                SMS: 32123 (FixMate)
              </li>
              <li className="flex items-center text-gray-300">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17.657 16l-2.473-2.473a4.999 4.999 0 01-1.414 1.414L16.243 17.657a1 1 0 001.414-1.414z"></path>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 12a2 2 0 100-4 2 2 0 000 4z"></path>
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 10a2 2 0 100-4 2 2 0 000 4z"></path>
                </svg>
                Cape Town, Johannesburg, Durban
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-gray-700 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-center md:text-left mb-4 md:mb-0">
              <p className="text-gray-400 text-sm">
                FixMate-SA is a product of Donald Shai Technologies (Pty) Ltd. All rights reserved.
              </p>
              <p className="text-gray-500 text-xs mt-1">
                Company Registration No: 2019/288556/07
              </p>
            </div>
            
            <div className="flex space-x-6">
              <Link to="/terms-of-service" className="text-gray-400 hover:text-white text-sm transition">
                Terms of Service
              </Link>
              <Link to="/privacy-policy" className="text-gray-400 hover:text-white text-sm transition">
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