import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { useNavigate } from 'react-router-dom';
import Logo from '../Common/Logo';
import EmergencyButton from '../Common/EmergencyButton';

const Header = () => {
  const { user, roleInfo, displayName, welcomeMessage, logout, getUserRole } = useAuth();
  const { currentLanguage, changeLanguage, getAvailableLanguageOptions } = useLanguage();
  const [showLanguageDropdown, setShowLanguageDropdown] = useState(false);
  const navigate = useNavigate();
  
  // Get available languages
  const availableLanguages = getAvailableLanguageOptions();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const availableLanguages = getAvailableLanguageOptions();
  const userRole = getUserRole();

  // Role-specific styling
  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-red-600';
      case 'fixer': return 'bg-orange-600';
      case 'client': return 'bg-blue-600';
      default: return 'bg-blue-600';
    }
  };

  const getRoleTextColor = (role) => {
    switch (role) {
      case 'admin': return 'text-red-600';
      case 'fixer': return 'text-orange-600';  
      case 'client': return 'text-blue-600';
      default: return 'text-blue-600';
    }
  };

  return (
    <header className={`${getRoleColor(userRole)} text-white shadow-lg`}>
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Logo 
              size="medium" 
              variant="header" 
              showText={true}
            />
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Welcome Message */}
            {welcomeMessage && (
              <div className="hidden md:flex items-center space-x-2">
                <div className="text-sm font-medium">
                  {welcomeMessage}
                </div>
                {userRole !== 'client' && (
                  <span className={`px-2 py-1 rounded-full text-xs font-bold bg-white ${getRoleTextColor(userRole)} uppercase`}>
                    {userRole}
                  </span>
                )}
              </div>
            )}
            
            {/* Emergency Button */}
            {user && (
              <EmergencyButton className="hidden sm:flex" />
            )}
            
            {/* Language Selector */}
            <div className="relative">
              <button
                onClick={() => setShowLanguageDropdown(!showLanguageDropdown)}
                className={`flex items-center space-x-2 ${getRoleColor(userRole)} hover:opacity-80 px-3 py-2 rounded-md text-sm font-medium transition-colors bg-black bg-opacity-20`}
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
                  <div className={`w-8 h-8 ${getRoleColor(userRole)} bg-opacity-80 rounded-full flex items-center justify-center`}>
                    <span className="text-white font-semibold text-sm">
                      {user.display_name ? user.display_name.charAt(0).toUpperCase() : user.first_name ? user.first_name.charAt(0).toUpperCase() : 'U'}
                    </span>
                  </div>
                  <div className="hidden sm:flex flex-col">
                    <span className="text-sm font-medium">{displayName || user.full_name || user.display_name || `${user.first_name} ${user.last_name}`}</span>
                    {roleInfo?.fixer_data && (
                      <span className="text-xs opacity-75">
                        ⭐ {roleInfo.fixer_data.rating.toFixed(1)} • {roleInfo.fixer_data.total_jobs} jobs
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={handleLogout}
                  className={`${getRoleColor(userRole)} hover:opacity-80 bg-black bg-opacity-20 px-3 py-1 rounded-md text-sm font-medium transition-colors`}
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