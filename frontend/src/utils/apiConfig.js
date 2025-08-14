// API URL utility for consistent backend URL handling across environments

const getBackendUrl = () => {
  // Always prefer the REACT_APP_BACKEND_URL environment variable if it exists
  if (process.env.REACT_APP_BACKEND_URL) {
    console.log('🔍 USING REACT_APP_BACKEND_URL:', process.env.REACT_APP_BACKEND_URL);
    return process.env.REACT_APP_BACKEND_URL;
  }
  
  // Fallback logic for different environments
  const currentHost = typeof window !== 'undefined' ? window.location.host : '';
  
  // Check if we're in the Emergent preview environment
  if (currentHost.includes('preview.emergentagent.com')) {
    // In Emergent preview, backend runs on same domain - use local backend
    console.log('🔍 EMERGENT PREVIEW MODE: Using same domain for local backend');
    return '';
  }
  
  // If we're in production (Heroku or other hosting), use relative URLs
  if (process.env.NODE_ENV === 'production') {
    console.log('🔍 PRODUCTION MODE: Using relative URLs for production deployment');
    return '';
  }
  
  // For local development, use localhost backend
  const devUrl = 'http://localhost:8001';
  console.log('🔍 LOCAL DEVELOPMENT MODE: Using backend URL:', devUrl);
  return devUrl;
};

export const BACKEND_URL = getBackendUrl();
export const API_BASE_URL = `${BACKEND_URL}/api`;

// Debug logging
console.log('🔍 API Configuration:', {
  NODE_ENV: process.env.NODE_ENV,
  BACKEND_URL,
  API_BASE_URL,
  REACT_APP_BACKEND_URL: process.env.REACT_APP_BACKEND_URL,
  CURRENT_HOST: typeof window !== 'undefined' ? window.location.host : 'server'
});

export default { BACKEND_URL, API_BASE_URL };