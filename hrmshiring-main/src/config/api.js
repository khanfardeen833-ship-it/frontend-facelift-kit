// API Configuration
export const API_CONFIG = {
  BASE_URL: 'http://localhost:5000', // Use localhost for development
  API_KEY: process.env.REACT_APP_API_KEY || 'sk-hiring-bot-2024-secret-key-xyz789',
  HEADERS: {
    'X-API-Key': process.env.REACT_APP_API_KEY || 'sk-hiring-bot-2024-secret-key-xyz789',
    'Content-Type': 'application/json'
  }
};

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    SIGNUP: '/api/auth/signup',
    VERIFY: '/api/auth/verify',
    PROFILE: '/api/auth/profile',
  },
  JOBS: {
    GET_APPROVED: '/api/jobs/approved',
    GET_DASHBOARD: '/api/jobs/dashboard',
    GET_HR_APPROVED: '/api/hr/jobs/approved',
    GET_BY_ID: (id) => `/api/jobs/${id}`,
    TOGGLE_VISIBILITY: (id) => `/api/jobs/${id}/toggle-visibility`,
  },
  STATS: {
    GET: '/api/stats',
    GET_HR: '/api/hr/stats',
  },
  TICKETS: {
    APPROVE: (id) => `/api/tickets/${id}/approve`,
    GET_RESUMES: (id) => `/api/tickets/${id}/resumes`,
    FILTER_RESUMES: (id) => `/api/tickets/${id}/filter-resumes`,
    GET_TOP_RESUMES: (id) => `/api/tickets/${id}/top-resumes`,
  },
  CHAT: {
    START: '/api/chat/start',
    MESSAGE: '/api/chat/message',
  }
};

// Helper function to get full URL
export const getApiUrl = (endpoint) => `${API_CONFIG.BASE_URL}${endpoint}`;

// Helper function to get headers
export const getHeaders = (contentType = 'application/json') => ({
  ...API_CONFIG.HEADERS,
  'Content-Type': contentType
});

// Helper function to get auth headers
export const getAuthHeaders = (token, contentType = 'application/json') => ({
  'Authorization': `Bearer ${token}`,
  'Content-Type': contentType
});

// Main API call function
export const makeAPICall = async (endpoint, options = {}) => {
  const url = endpoint.startsWith('http') ? endpoint : `${API_CONFIG.BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    method: 'GET',
    headers: {
      'X-API-Key': API_CONFIG.API_KEY,
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      ...options.headers
    }
  };

  const finalOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers
    }
  };

  console.log('🌐 Making API call to:', url);
  console.log('🔑 Headers:', finalOptions.headers);

  try {
    const response = await fetch(url, finalOptions);
    console.log('📡 Response status:', response.status, response.statusText);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('📦 Response data:', data);
    
    return data;
  } catch (error) {
    console.error('❌ API call failed:', error);
    throw error;
  }
};
