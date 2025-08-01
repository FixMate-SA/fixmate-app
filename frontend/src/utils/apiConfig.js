// API URL utility for consistent backend URL handling across environments

const getBackendUrl = () => {
  // If we're in production (Heroku), use relative URLs since frontend and backend are on same domain
  if (process.env.NODE_ENV === 'production') {
    console.log('🔍 PRODUCTION MODE: Using relative URLs for Heroku');
    return '';
  }
  
  // For development, use the environment variable
  const devUrl = process.env.REACT_APP_BACKEND_URL || '';
  console.log('🔍 DEVELOPMENT MODE: Using backend URL:', devUrl);
  return devUrl;
};

export const BACKEND_URL = getBackendUrl();
export const API_BASE_URL = `${BACKEND_URL}/api`;

// Debug logging
console.log('🔍 API Configuration:', {
  NODE_ENV: process.env.NODE_ENV,
  BACKEND_URL,
  API_BASE_URL,
  REACT_APP_BACKEND_URL: process.env.REACT_APP_BACKEND_URL
});

export default { BACKEND_URL, API_BASE_URL };