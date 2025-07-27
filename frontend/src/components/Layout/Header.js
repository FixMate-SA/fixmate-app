import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const { user, logout } = useAuth();
  const { currentLanguage, changeLanguage, getAvailableLanguageOptions } = useLanguage();
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const availableLanguages = getAvailableLanguageOptions();

  return (
    <header className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center">
                <span className="text-blue-600 font-bold text-lg">F</span>
              </div>
              <h1 className="text-xl font-bold">FixMate-SA</h1>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Language Selector */}
            <div className="relative">
              <button
                onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
                className="flex items-center space-x-2 bg-blue-700 hover:bg-blue-800 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              >
                <span>{availableLanguages.find(lang => lang.code === currentLanguage)?.flag || '🇿🇦'}</span>
                <span className="hidden sm:inline">{currentLanguage.toUpperCase()}</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {showLanguageDropdown && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-50">
                  <div className="py-1">
                    {availableLanguages.map((language) => (
                      <button
                        key={language.code}
                        onClick={() => {
                          changeLanguage(language.code);
                          setShowLanguageDropdown(false);
                        }}
                        className={`flex items-center space-x-3 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 ${
                          currentLanguage === language.code ? 'bg-blue-50 text-blue-600' : ''
                        }`}
                      >
                        <span className="text-lg">{language.flag}</span>
                        <span>{language.name}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {user && (
              <>
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-blue-700 rounded-full flex items-center justify-center">
                    <span className="text-white font-semibold text-sm">
                      {user.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <span className="hidden sm:inline-block text-sm">{user.name}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="bg-blue-700 hover:bg-blue-800 px-3 py-1 rounded-md text-sm font-medium transition-colors"
                >
                  Logout
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;