// API URL utility for consistent backend URL handling across environments
// Version 2.5.0 - ENVIRONMENT VARIABLE INDEPENDENT - 2025-01-14

const getBackendUrl = () => {
  // Get current environment information - with fallbacks for undefined values
  const currentHost = typeof window !== 'undefined' ? window.location.host : '';
  const nodeEnv = process.env.NODE_ENV || 'development';
  const reactAppBackendUrl = process.env.REACT_APP_BACKEND_URL || '';
  
  console.log('🔍 ENVIRONMENT VARIABLE INDEPENDENT Detection:', {
    currentHost,
    nodeEnv,
    reactAppBackendUrl: reactAppBackendUrl || 'UNDEFINED/EMPTY',
    processEnvKeys: Object.keys(process.env).filter(key => key.startsWith('REACT_APP')),
    NODE_ENV: process.env.NODE_ENV
  });
  
  // SOLUTION: Make application completely independent of environment variables
  
  // 1. LOCAL DEVELOPMENT: Detect by port and host patterns
  if (currentHost.includes('localhost') || currentHost.includes('127.0.0.1') || currentHost.includes(':3000')) {
    const devUrl = 'http://localhost:8001';
    console.log('🔍 LOCAL DEVELOPMENT (PORT-BASED): Using backend URL:', devUrl);
    return devUrl;
  }
  
  // 2. EMERGENT PREVIEW: Detect by domain pattern  
  if (currentHost.includes('preview.emergentagent.com')) {
    // For preview, try to use environment variable if available and valid
    if (reactAppBackendUrl && reactAppBackendUrl.includes('preview.emergentagent.com')) {
      console.log('🔍 VALID PREVIEW ENVIRONMENT: Using REACT_APP_BACKEND_URL:', reactAppBackendUrl);
      return reactAppBackendUrl;
    } else {
      console.log('🔍 PREVIEW ENVIRONMENT - NO ENV VAR: Using relative URLs');
      return '';
    }
  }
  
  // 3. HEROKU PRODUCTION: Detect by herokuapp.com or any other production pattern
  if (currentHost.includes('herokuapp.com') || nodeEnv === 'production' || currentHost.includes('.com')) {
    console.log('🚨 PRODUCTION ENVIRONMENT DETECTED (ENV VAR INDEPENDENT)');
    console.log('🚨 FORCING RELATIVE URLS - IGNORING ALL ENVIRONMENT VARIABLES');
    console.log('🚨 Production domain:', currentHost);
    return '';
  }
  
  // 4. FALLBACK: Always use relative URLs for unknown environments
  console.log('🔍 FALLBACK (ENV VAR INDEPENDENT): Using relative URLs');
  return '';
};

export const BACKEND_URL = getBackendUrl();
export const API_BASE_URL = `${BACKEND_URL}/api`;

// ENVIRONMENT VARIABLE INDEPENDENT STATUS
console.log('🚨 ENVIRONMENT VARIABLE INDEPENDENT CONFIGURATION:', {
  DETECTED_ENVIRONMENT: (() => {
    const host = typeof window !== 'undefined' ? window.location.host : '';
    if (host.includes('localhost')) return 'LOCAL_DEVELOPMENT';
    if (host.includes('preview.emergentagent.com')) return 'PREVIEW_ENVIRONMENT';
    if (host.includes('herokuapp.com')) return 'HEROKU_PRODUCTION';
    if (host.includes('.com')) return 'PRODUCTION_DOMAIN';
    return 'UNKNOWN';
  })(),
  CURRENT_HOST: typeof window !== 'undefined' ? window.location.host : 'server',
  NODE_ENV: process.env.NODE_ENV || 'UNDEFINED',
  REACT_APP_BACKEND_URL: process.env.REACT_APP_BACKEND_URL || 'UNDEFINED',
  FINAL_BACKEND_URL: BACKEND_URL,
  FINAL_API_BASE_URL: API_BASE_URL,
  HEROKU_READY: BACKEND_URL === '',
  SOLUTION_STATUS: BACKEND_URL === '' ? '✅ RELATIVE URLS (WORKS WITHOUT ENV VARS)' : '⚠️ ABSOLUTE URL (REQUIRES ENV VARS)'
});

// Production API endpoint verification
if (typeof window !== 'undefined') {
  const testEndpoints = {
    'Dashboard API': `${API_BASE_URL}/dashboard/user-id`,
    'Jobs API': `${API_BASE_URL}/fixer/available-jobs`,
    'Notifications API': `${API_BASE_URL}/fixer/notifications`,
    'Payment API': `${API_BASE_URL}/fixer/outstanding-payments`,
    'Auth API': `${API_BASE_URL}/auth/login`
  };
  
  console.log('🧪 ENVIRONMENT INDEPENDENT API ENDPOINTS:', testEndpoints);
  
  // Check if we're in a problematic environment
  const hasEnvironmentIssues = !process.env.NODE_ENV || !Object.keys(process.env).some(key => key.startsWith('REACT_APP'));
  if (hasEnvironmentIssues) {
    console.log('⚠️ ENVIRONMENT VARIABLE ISSUES DETECTED:');
    console.log('   - NODE_ENV:', process.env.NODE_ENV || 'UNDEFINED');
    console.log('   - REACT_APP_* variables:', Object.keys(process.env).filter(key => key.startsWith('REACT_APP')).length);
    console.log('✅ SOLUTION: Using domain-based detection instead of environment variables');
  }
}

export default { BACKEND_URL, API_BASE_URL };