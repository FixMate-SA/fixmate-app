import React from 'react';

const Logo = ({ 
  size = 'medium', 
  className = '',
  showText = true,
  variant = 'default' // default, header, login, dashboard
}) => {
  const sizeClasses = {
    small: 'w-8 h-8',
    medium: 'w-12 h-12', 
    large: 'w-16 h-16',
    xlarge: 'w-24 h-24'
  };

  const textSizeClasses = {
    small: 'text-lg',
    medium: 'text-xl',
    large: 'text-2xl', 
    xlarge: 'text-4xl'
  };

  const getVariantStyles = () => {
    switch (variant) {
      case 'header':
        return {
          container: 'flex items-center space-x-3',
          text: 'font-bold text-white'
        };
      case 'login':
        return {
          container: 'flex flex-col items-center space-y-4 mb-8',
          text: 'font-bold text-gray-800 text-center'
        };
      case 'dashboard':
        return {
          container: 'flex items-center space-x-2',
          text: 'font-semibold text-gray-700'
        };
      default:
        return {
          container: 'flex items-center space-x-2',
          text: 'font-bold text-gray-800'
        };
    }
  };

  const variantStyles = getVariantStyles();

  return (
    <div className={`${variantStyles.container} ${className}`}>
      <img 
        src="/fixmate-logo.jpg" 
        alt="FixMate-SA Logo"
        className={`${sizeClasses[size]} object-contain rounded-lg shadow-sm`}
      />
      {showText && (
        <div className={variant === 'login' ? 'flex flex-col items-center' : ''}>
          <span className={`${textSizeClasses[size]} ${variantStyles.text}`}>
            FixMate-SA
          </span>
          {variant === 'login' && (
            <span className="text-sm text-gray-600 mt-1">
              South Africa's Premier Service Platform
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default Logo;