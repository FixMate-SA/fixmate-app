import React from 'react';
import { useNavigate } from 'react-router-dom';

const BackButton = ({ text = "← Back to Dashboard", className = "" }) => {
  const navigate = useNavigate();

  const handleBack = () => {
    // Try to go back in history first
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      // Fallback to dashboard
      navigate('/dashboard');
    }
  };

  return (
    <button
      onClick={handleBack}
      className={`inline-flex items-center px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 hover:text-gray-900 transition-colors duration-200 ${className}`}
    >
      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7"></path>
      </svg>
      {text}
    </button>
  );
};

export default BackButton;