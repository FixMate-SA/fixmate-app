// API URL utility for consistent backend URL handling across environments

const getBackendUrl = () => {
  // Get current environment information
  const currentHost = typeof window !== 'undefined' ? window.location.host : '';
  const isProduction = process.env.NODE_ENV === 'production';
  const reactAppBackendUrl = process.env.REACT_APP_BACKEND_URL;
  
  console.log('🔍 Environment Detection:', {
    currentHost,
    isProduction,
    reactAppBackendUrl,
    NODE_ENV: process.env.NODE_ENV
  });
  
  // Check if we're in a production environment that's NOT the preview environment
  const isHerokuOrExternalProduction = isProduction && !currentHost.includes('preview.emergentagent.com');
  
  if (isHerokuOrExternalProduction) {
    // For Heroku or other external production deployments, use relative URLs
    console.log('🔍 HEROKU/EXTERNAL PRODUCTION MODE: Using relative URLs for same-domain backend');
    return '';
  }
  
  // If we have REACT_APP_BACKEND_URL and we're in preview environment, use it
  if (reactAppBackendUrl && currentHost.includes('preview.emergentagent.com')) {
    console.log('🔍 PREVIEW ENVIRONMENT: Using REACT_APP_BACKEND_URL:', reactAppBackendUrl);
    return reactAppBackendUrl;
  }
  
  // For local development, use localhost backend
  if (!isProduction) {
    const devUrl = 'http://localhost:8001';
    console.log('🔍 LOCAL DEVELOPMENT: Using backend URL:', devUrl);
    return devUrl;
  }
  
  // Final fallback for any other production scenario
  console.log('🔍 DEFAULT PRODUCTION: Using relative URLs');
  return '';
};

export const BACKEND_URL = getBackendUrl();
export const API_BASE_URL = `${BACKEND_URL}/api`;

// Debug logging
console.log('🔍 Final API Configuration:', {
  NODE_ENV: process.env.NODE_ENV,
  BACKEND_URL,
  API_BASE_URL,
  REACT_APP_BACKEND_URL: process.env.REACT_APP_BACKEND_URL,
  CURRENT_HOST: typeof window !== 'undefined' ? window.location.host : 'server'
});

export default { BACKEND_URL, API_BASE_URL };