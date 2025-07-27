import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useLanguage } from '../../contexts/LanguageContext';

const Navigation = () => {
  const location = useLocation();
  const { t } = useLanguage();

  const navItems = [
    { path: '/', label: t('dashboard', 'Dashboard'), icon: '📊' },
    { path: '/jobs', label: t('jobs', 'Jobs'), icon: '📋' },
    { path: '/fixers', label: t('fixers', 'Fixers'), icon: '🔧' },
    { path: '/learning', label: t('learning', 'Learning'), icon: '🎓' },
    { path: '/sms', label: 'SMS Portal', icon: '📱' },
    { path: '/enterprise', label: 'Enterprise', icon: '🏢' },
    { path: '/payment', label: 'Payments', icon: '💳' },
    { path: '/profile', label: t('profile', 'Profile'), icon: '👤' },
  ];

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex space-x-2 overflow-x-auto">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-2 py-4 px-3 border-b-2 transition-colors whitespace-nowrap ${
                isActive(item.path)
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="font-medium text-sm">{item.label}</span>
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;