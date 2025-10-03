import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { getApiUrl, getAuthHeaders, API_ENDPOINTS } from '../config/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // API configuration is now centralized in config/api.js

  // Check if user is logged in on app start
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      verifyToken(token);
    } else {
      setLoading(false);
    }
  }, []);

  const verifyToken = async (token) => {
    try {
      const response = await axios.post(getApiUrl(API_ENDPOINTS.AUTH.VERIFY), { token });
      if (response.data.success) {
        const userData = response.data.data;
        setUser({
          user_id: userData.user_id,
          email: userData.email,
          role: userData.role
        });
        
        // Fetch full profile after token verification
        try {
          const profileData = await getProfile();
          if (profileData) {
            setUser(prev => ({ ...prev, ...profileData }));
          }
        } catch (error) {
          console.warn('Could not fetch profile after token verification:', error);
        }
      } else {
        localStorage.removeItem('token');
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      setError(null);
      const response = await axios.post(getApiUrl(API_ENDPOINTS.AUTH.LOGIN), {
        email,
        password
      });

      if (response.data.success) {
        const { token, ...userData } = response.data.data;
        localStorage.setItem('token', token);
        setUser(userData);
        
        // Fetch full profile after login
        try {
          const profileData = await getProfile();
          if (profileData) {
            setUser(prev => ({ ...prev, ...profileData }));
          }
        } catch (error) {
          console.warn('Could not fetch profile after login:', error);
        }
        
        return { success: true };
      } else {
        setError(response.data.error);
        return { success: false, error: response.data.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Login failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const signup = async (userData) => {
    try {
      setError(null);
      const response = await axios.post(getApiUrl(API_ENDPOINTS.AUTH.SIGNUP), userData);

      if (response.data.success) {
        const { token, ...userInfo } = response.data.data;
        localStorage.setItem('token', token);
        setUser(userInfo);
        return { success: true };
      } else {
        setError(response.data.error);
        return { success: false, error: response.data.error };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Signup failed. Please try again.';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setError(null);
  };

  const getProfile = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return null;

      const response = await axios.get(getApiUrl(API_ENDPOINTS.AUTH.PROFILE), {
        headers: getAuthHeaders(token)
      });

      if (response.data.success) {
        return response.data.data;
      }
      return null;
    } catch (error) {
      console.error('Failed to get profile:', error);
      return null;
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    signup,
    logout,
    getProfile,
    isAuthenticated: !!user
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
