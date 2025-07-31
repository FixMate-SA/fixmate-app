import React from 'react';

const LoadingSpinner = ({ message = "Loading...", size = "medium" }) => {
  const sizeClasses = {
    small: "h-8 w-8",
    medium: "h-12 w-12", 
    large: "h-16 w-16"
  };

  return (
    <div className="flex items-center justify-center p-8">
      <div className="text-center">
        <div 
          className={`animate-spin rounded-full border-b-2 border-blue-600 mx-auto mb-3 ${sizeClasses[size]}`}
        ></div>
        <div className="text-gray-600 text-sm font-medium">{message}</div>
      </div>
    </div>
  );
};

export default LoadingSpinner;