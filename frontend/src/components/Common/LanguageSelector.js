import React, { useState } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';
import { getLanguageNames } from '../../locales/languages';

const LanguageSelector = ({ className = '' }) => {
  const { currentLanguage, changeLanguage } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const languages = getLanguageNames();

  const handleLanguageSelect = (languageCode) => {
    changeLanguage(languageCode);
    setIsOpen(false);
  };

  const currentLang = languages.find(lang => lang.code === currentLanguage);

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <span className="text-lg">{currentLang?.flag}</span>
        <span className="text-sm font-medium text-gray-700">
          {currentLang?.name}
        </span>
        <svg
          className={`w-4 h-4 text-gray-500 transform transition-transform ${
            isOpen ? 'rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-80 overflow-y-auto">
          <div className="py-2">
            <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase tracking-wide bg-gray-50">
              South African Languages
            </div>
            
            {languages.map((language) => (
              <button
                key={language.code}
                onClick={() => handleLanguageSelect(language.code)}
                className={`w-full text-left px-4 py-3 flex items-center gap-3 hover:bg-blue-50 transition-colors ${
                  currentLanguage === language.code 
                    ? 'bg-blue-100 text-blue-900 font-medium' 
                    : 'text-gray-700'
                }`}
              >
                <span className="text-lg flex-shrink-0">{language.flag}</span>
                <div className="flex-1">
                  <div className="font-medium">{language.name}</div>
                  <div className="text-xs text-gray-500">
                    {getLanguageDescription(language.code)}
                  </div>
                </div>
                
                {currentLanguage === language.code && (
                  <svg
                    className="w-4 h-4 text-blue-600 flex-shrink-0"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                )}
              </button>
            ))}
          </div>
          
          <div className="px-3 py-2 border-t border-gray-100 bg-gray-50">
            <p className="text-xs text-gray-500 text-center">
              All 11 official languages of South Africa supported
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

// Helper function to provide language descriptions
function getLanguageDescription(code) {
  const descriptions = {
    en: 'English - Official',
    af: 'Afrikaans - Official',
    nso: 'Sepedi - Limpopo & Gauteng',
    zu: 'isiZulu - Most spoken',
    ts: 'Xitsonga - Limpopo',
    xh: 'isiXhosa - Eastern Cape',
    st: 'Sesotho - Free State',
    tn: 'Setswana - North West',
    ve: 'Tshivenda - Limpopo',
    nr: 'isiNdebele - Mpumalanga',
    ss: 'siSwati - Mpumalanga'
  };
  return descriptions[code] || 'Official Language';
}

export default LanguageSelector;