// API URL utility for consistent backend URL handling across environments
// Version 2.3.0 - Heroku Production Fix Enhanced - Updated: 2025-01-14

const getBackendUrl = () => {
  // Get current environment information
  const currentHost = typeof window !== 'undefined' ? window.location.host : '';
  const isProduction = process.env.NODE_ENV === 'production';
  const reactAppBackendUrl = process.env.REACT_APP_BACKEND_URL;
  
  console.log('🔍 Enhanced Environment Detection:', {
    currentHost,
    isProduction,
    reactAppBackendUrl,
    NODE_ENV: process.env.NODE_ENV
  });
  
  // Priority 1: Detect Heroku or other external production (override any environment variable)
  const isHerokuOrExternalProduction = isProduction && !currentHost.includes('preview.emergentagent.com');
  
  if (isHerokuOrExternalProduction) {
    // CRITICAL: For Heroku production, ALWAYS use relative URLs regardless of environment variable
    console.log('🔍 HEROKU/EXTERNAL PRODUCTION MODE (FORCED): Using relative URLs for same-domain backend');
    console.log('🔧 OVERRIDING environment variable for Heroku production compatibility');
    return '';
  }
  
  // Priority 2: Preview environment with valid preview URL
  if (currentHost.includes('preview.emergentagent.com') && reactAppBackendUrl && reactAppBackendUrl.includes('preview.emergentagent.com')) {
    console.log('🔍 PREVIEW ENVIRONMENT: Using REACT_APP_BACKEND_URL:', reactAppBackendUrl);
    return reactAppBackendUrl;
  }
  
  // Priority 3: Preview environment but environment variable might be wrong - use relative URLs
  if (currentHost.includes('preview.emergentagent.com')) {
    console.log('🔍 PREVIEW ENVIRONMENT (FALLBACK): Using relative URLs due to invalid REACT_APP_BACKEND_URL');
    return '';
  }
  
  // Priority 4: Local development
  if (!isProduction) {
    const devUrl = 'http://localhost:8001';
    console.log('🔍 LOCAL DEVELOPMENT: Using backend URL:', devUrl);
    return devUrl;
  }
  
  // Final fallback for any other production scenario
  console.log('🔍 FALLBACK PRODUCTION: Using relative URLs');
  return '';
};

export const BACKEND_URL = getBackendUrl();
export const API_BASE_URL = `${BACKEND_URL}/api`;

// Enhanced debug logging with solutions
console.log('🔍 Final Enhanced API Configuration:', {
  NODE_ENV: process.env.NODE_ENV,
  BACKEND_URL,
  API_BASE_URL,
  REACT_APP_BACKEND_URL: process.env.REACT_APP_BACKEND_URL,
  CURRENT_HOST: typeof window !== 'undefined' ? window.location.host : 'server',
  CONFIGURATION_STATUS: BACKEND_URL === '' ? 'RELATIVE_URLS (Production/Heroku)' : 'ABSOLUTE_URL (Dev/Preview)'
});

// Add runtime configuration test
if (typeof window !== 'undefined') {
  console.log('🧪 Runtime API Configuration Test:', {
    'Sample API URL': `${API_BASE_URL}/fixer/outstanding-payments`,
    'Expected to work': BACKEND_URL === '' ? 'Yes (relative to current domain)' : 'Yes (absolute URL)',
    'Troubleshooting': BACKEND_URL === '' ? 'API calls will use current domain' : 'API calls will use specific backend URL'
  });
}

export default { BACKEND_URL, API_BASE_URL };