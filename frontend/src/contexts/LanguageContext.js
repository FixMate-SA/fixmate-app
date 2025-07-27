import React, { createContext, useState, useContext, useEffect } from 'react';
import { getLanguage, getAvailableLanguages, getLanguageNames } from '../locales/languages';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [translations, setTranslations] = useState(getLanguage('en').translations);

  useEffect(() => {
    // Load saved language preference
    const savedLanguage = localStorage.getItem('fixmate_language');
    if (savedLanguage && getAvailableLanguages().includes(savedLanguage)) {
      changeLanguage(savedLanguage);
    } else {
      // Auto-detect language from browser or location
      const browserLanguage = navigator.language.split('-')[0];
      if (getAvailableLanguages().includes(browserLanguage)) {
        changeLanguage(browserLanguage);
      }
    }
  }, []);

  const changeLanguage = (languageCode) => {
    if (getAvailableLanguages().includes(languageCode)) {
      setCurrentLanguage(languageCode);
      setTranslations(getLanguage(languageCode).translations);
      localStorage.setItem('fixmate_language', languageCode);
    }
  };

  const t = (key, fallback = key) => {
    return translations[key] || fallback;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-ZA', {
      style: 'currency',
      currency: 'ZAR'
    }).format(amount);
  };

  const formatDate = (date) => {
    return new Intl.DateTimeFormat(currentLanguage === 'en' ? 'en-ZA' : currentLanguage, {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    }).format(new Date(date));
  };

  const formatTime = (date) => {
    return new Intl.DateTimeFormat(currentLanguage === 'en' ? 'en-ZA' : currentLanguage, {
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(date));
  };

  const getLanguageInfo = () => {
    return getLanguage(currentLanguage);
  };

  const getAvailableLanguageOptions = () => {
    return getLanguageNames();
  };

  const isRTL = () => {
    // Add RTL languages if needed (Arabic, Hebrew, etc.)
    return false;
  };

  const value = {
    currentLanguage,
    translations,
    changeLanguage,
    t,
    formatCurrency,
    formatDate,
    formatTime,
    getLanguageInfo,
    getAvailableLanguageOptions,
    isRTL
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};