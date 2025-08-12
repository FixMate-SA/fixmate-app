// API URL utility for consistent backend URL handling across environments

const getBackendUrl = () => {
  // If we're in production (Heroku), use relative URLs since frontend and backend are on same domain
  if (process.env.NODE_ENV === 'production') {
    console.log('🔍 PRODUCTION MODE: Using relative URLs for Heroku');
    return '';
  }
  
  // For development/preview, check if we're in the Emergent preview environment
  const currentHost = typeof window !== 'undefined' ? window.location.host : '';
  
  if (currentHost.includes('preview.emergentagent.com')) {
    // In Emergent preview, backend runs on same domain
    console.log('🔍 EMERGENT PREVIEW MODE: Using same domain for backend');
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