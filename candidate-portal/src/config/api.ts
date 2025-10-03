// API Configuration
export const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

export const API_ENDPOINTS = {
  JOBS: '/api/jobs/approved',
  APPLICATIONS: {
    BASE: '/api/applications',
    SUBMIT: (jobId: string) => `/api/applications/${jobId}/submit`
  },
  UPLOAD: '/api/upload'
};

export const getApiUrl = (endpoint: string) => `${API_BASE_URL}${endpoint}`;

export const getHeaders = (contentType?: string) => ({
  'Content-Type': contentType || 'application/json',
  'Accept': 'application/json'
});

export const getAuthHeaders = (token?: string) => ({
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  ...(token && { 'Authorization': `Bearer ${token}` })
});