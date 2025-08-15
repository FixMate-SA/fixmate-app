// API URL utility for consistent backend URL handling across environments
// Version 2.4.0 - DEFINITIVE Heroku Production Fix - 2025-01-14

const getBackendUrl = () => {
  // Get current environment information
  const currentHost = typeof window !== 'undefined' ? window.location.host : '';
  const isProduction = process.env.NODE_ENV === 'production';
  const reactAppBackendUrl = process.env.REACT_APP_BACKEND_URL;
  
  console.log('🔍 DEFINITIVE Environment Detection:', {
    currentHost,
    isProduction,
    reactAppBackendUrl,
    NODE_ENV: process.env.NODE_ENV
  });
  
  // CRITICAL: Definitive Heroku production detection
  const isHerokuProduction = isProduction && (
    currentHost.includes('herokuapp.com') ||
    currentHost.includes('herokuapp.com') ||
    !currentHost.includes('preview.emergentagent.com')
  );
  
  if (isHerokuProduction) {
    // FORCE: Always use relative URLs for Heroku production, completely ignore environment variable
    console.log('🚨 DEFINITIVE HEROKU PRODUCTION DETECTED - FORCING RELATIVE URLS');
    console.log('🚨 COMPLETELY IGNORING REACT_APP_BACKEND_URL for Heroku production');
    console.log('🚨 API calls will use current domain:', currentHost);
    return '';
  }
  
  // For preview environment: Only use env var if we're actually in preview domain
  if (currentHost.includes('preview.emergentagent.com')) {
    if (reactAppBackendUrl && reactAppBackendUrl.includes('preview.emergentagent.com')) {
      console.log('🔍 VALID PREVIEW ENVIRONMENT: Using REACT_APP_BACKEND_URL:', reactAppBackendUrl);
      return reactAppBackendUrl;
    } else {
      console.log('🔍 PREVIEW ENVIRONMENT - INVALID ENV VAR: Using relative URLs');
      return '';
    }
  }
  
  // For local development: Use localhost
  if (!isProduction) {
    const devUrl = 'http://localhost:8001';
    console.log('🔍 LOCAL DEVELOPMENT: Using backend URL:', devUrl);
    return devUrl;
  }
  
  // Final fallback: relative URLs
  console.log('🔍 FALLBACK: Using relative URLs');
  return '';
};

export const BACKEND_URL = getBackendUrl();
export const API_BASE_URL = `${BACKEND_URL}/api`;

// DEFINITIVE debug logging
console.log('🚨 DEFINITIVE API Configuration Status:', {
  NODE_ENV: process.env.NODE_ENV,
  CURRENT_HOST: typeof window !== 'undefined' ? window.location.host : 'server',
  REACT_APP_BACKEND_URL: process.env.REACT_APP_BACKEND_URL,
  FINAL_BACKEND_URL: BACKEND_URL,
  FINAL_API_BASE_URL: API_BASE_URL,
  HEROKU_DETECTED: process.env.NODE_ENV === 'production' && !window.location.host.includes('preview.emergentagent.com'),
  SOLUTION_STATUS: BACKEND_URL === '' ? '✅ USING RELATIVE URLS (HEROKU SAFE)' : '⚠️ USING ABSOLUTE URL'
});

// Runtime API test for production debugging
if (typeof window !== 'undefined' && process.env.NODE_ENV === 'production') {
  console.log('🧪 PRODUCTION API ENDPOINT TEST:', {
    'Payment API': `${API_BASE_URL}/fixer/outstanding-payments`,
    'Dashboard API': `${API_BASE_URL}/dashboard/${window.location.pathname.includes('fixer') ? 'fixer-id' : 'user-id'}`,
    'Authentication': `${API_BASE_URL}/auth/login`,
    'Expected Result': BACKEND_URL === '' ? 'SUCCESS - Will use current domain' : 'MAY FAIL - Using external URL'
  });
}

export default { BACKEND_URL, API_BASE_URL };