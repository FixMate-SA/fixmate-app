import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../../contexts/LanguageContext';
import Logo from '../Common/Logo';

const Footer = () => {
  const { t } = useLanguage();
  const navigate = useNavigate();

  return (
    <footer className="bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="py-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Logo and Company Info */}
            <div className="col-span-1 md:col-span-2">
              <Logo 
                size="medium" 
                variant="default" 
                showText={true}
                className="mb-4"
              />
              <p className="text-gray-300 text-sm max-w-md">
                {t('footerDescription', 'South Africa\'s premier service marketplace connecting skilled fixers with clients across all 11 official languages. Professional, reliable, and trusted by thousands.')}
              </p>
              <div className="flex space-x-4 mt-4">
                <span className="text-sm text-gray-400">🇿🇦 Proudly South African</span>
                <span className="text-sm text-gray-400">🌍 11 Languages</span>
              </div>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-lg font-semibold mb-4">{t('quickLinks', 'Quick Links')}</h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li><a href="#" className="hover:text-white transition-colors">{t('aboutUs', 'About Us')}</a></li>
                <li><a href="#" className="hover:text-white transition-colors">{t('howItWorks', 'How It Works')}</a></li>
                <li><a href="#" className="hover:text-white transition-colors">{t('safety', 'Safety & Trust')}</a></li>
                <li><a href="#" className="hover:text-white transition-colors">{t('becomeAFixer', 'Become a Fixer')}</a></li>
                <li><a href="#" className="hover:text-white transition-colors">{t('helpCenter', 'Help Center')}</a></li>
              </ul>
            </div>

            {/* Contact & Support */}
            <div>
              <h3 className="text-lg font-semibold mb-4">{t('support', 'Support')}</h3>
              <ul className="space-y-2 text-sm text-gray-300">
                <li className="flex items-center space-x-2">
                  <span>📱</span>
                  <span>+27 (0) 11 123 4567</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span>📧</span>
                  <span>support@fixmate-sa.com</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span>💬</span>
                  <span>SMS: 32123 (FixMate)</span>
                </li>
                <li className="flex items-center space-x-2">
                  <span>🏢</span>
                  <span>Cape Town, Johannesburg, Durban</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-gray-700 mt-8 pt-6">
            {/* Legal Information Block */}
            <div className="text-center mb-6">
              <p className="font-semibold text-white mb-2">
                FixMate-SA is a product of Donald Shai Technologies (Pty) Ltd. All rights reserved
              </p>
              <p className="text-sm text-gray-400">
                Company Registration No: 2019/203656/07
              </p>
              <div className="mt-4 flex justify-center space-x-4 text-sm">
                <button
                  onClick={() => navigate('/terms')}
                  className="text-gray-300 hover:text-white transition-colors font-medium"
                >
                  Terms of Service
                </button>
                <span className="text-gray-500">|</span>
                <button
                  onClick={() => navigate('/privacy')}
                  className="text-gray-300 hover:text-white transition-colors font-medium"
                >
                  Privacy Policy
                </button>
              </div>
            </div>
            
            {/* Copyright Bar */}
            <div className="flex flex-col md:flex-row justify-between items-center border-t border-gray-600 pt-4">
              <div className="text-sm text-gray-400">
                © 2025 FixMate-SA. {t('allRightsReserved', 'All rights reserved.')} {' '}
                <span className="ml-4">
                  {t('builtForSA', 'Built with ❤️ for South Africa')}
                </span>
              </div>
              
              <div className="flex space-x-6 mt-4 md:mt-0 text-sm text-gray-400">
                <button
                  onClick={() => navigate('/privacy')}
                  className="hover:text-white transition-colors"
                >
                  {t('privacy', 'Privacy Policy')}
                </button>
                <button
                  onClick={() => navigate('/terms')}
                  className="hover:text-white transition-colors"
                >
                  {t('terms', 'Terms of Service')}
                </button>
                <a href="#" className="hover:text-white transition-colors">{t('cookies', 'Cookie Policy')}</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;