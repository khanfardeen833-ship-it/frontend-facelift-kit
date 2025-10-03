// API Configuration
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000',
  API_KEY: process.env.REACT_APP_API_KEY || 'sk-hiring-bot-2024-secret-key-xyz789',
  HEADERS: {
    'X-API-Key': process.env.REACT_APP_API_KEY || 'sk-hiring-bot-2024-secret-key-xyz789',
    'Content-Type': 'application/json'
  }
};

// API endpoints
export const API_ENDPOINTS = {
  JOBS: {
    GET_APPROVED: '/api/jobs/approved',
    GET_BY_ID: (id) => `/api/jobs/${id}`,
  },
  APPLICATIONS: {
    SUBMIT: (jobId) => `/api/tickets/${jobId}/resumes`,
  }
};

// Helper function to get full URL
export const getApiUrl = (endpoint) => `${API_CONFIG.BASE_URL}${endpoint}`;

// Helper function to get headers
export const getHeaders = (contentType = 'application/json') => ({
  ...API_CONFIG.HEADERS,
  'Content-Type': contentType
});
