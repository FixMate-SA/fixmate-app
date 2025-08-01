// API URL utility for consistent backend URL handling across environments

const getBackendUrl = () => {
  // If we're in production (Heroku), use relative URLs since frontend and backend are on same domain
  if (process.env.NODE_ENV === 'production') {
    return '';
  }
  
  // For development, use the environment variable
  return process.env.REACT_APP_BACKEND_URL || '';
};

export const BACKEND_URL = getBackendUrl();
export const API_BASE_URL = `${BACKEND_URL}/api`;

export default { BACKEND_URL, API_BASE_URL };