import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useLanguage } from '../../contexts/LanguageContext';
import Logo from '../Common/Logo';

const Footer = () => {
  const { t } = useLanguage();

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
          <div className="border-t border-gray-700 mt-8 pt-6 flex flex-col md:flex-row justify-between items-center">
            <div className="text-sm text-gray-400">
              © 2025 FixMate-SA. {t('allRightsReserved', 'All rights reserved.')} {' '}
              <span className="ml-4">
                {t('builtForSA', 'Built with ❤️ for South Africa')}
              </span>
            </div>
            
            <div className="flex space-x-6 mt-4 md:mt-0 text-sm text-gray-400">
              <a href="#" className="hover:text-white transition-colors">{t('privacy', 'Privacy Policy')}</a>
              <a href="#" className="hover:text-white transition-colors">{t('terms', 'Terms of Service')}</a>
              <a href="#" className="hover:text-white transition-colors">{t('cookies', 'Cookie Policy')}</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;