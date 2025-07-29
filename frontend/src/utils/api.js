// API URL helper for Heroku deployment
export const getApiUrl = (endpoint = '') => {
  const baseUrl = process.env.REACT_APP_BACKEND_URL || '';
  const apiPath = '/api';
  
  if (baseUrl) {
    return `${baseUrl}${apiPath}${endpoint}`;
  }
  
  // For Heroku deployment where frontend and backend are served from the same domain
  return `${apiPath}${endpoint}`;
};

export const API_BASE_URL = getApiUrl();