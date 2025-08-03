import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../utils/apiConfig';

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
  const [roleInfo, setRoleInfo] = useState(null);
  const [displayName, setDisplayName] = useState('');
  const [welcomeMessage, setWelcomeMessage] = useState('');
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  const API_BASE = API_BASE_URL;

  useEffect(() => {
    // Check for stored auth data on app load
    console.log('AuthContext: Checking stored auth data...');
    const storedUser = localStorage.getItem('fixmate_user');
    const storedRoleInfo = localStorage.getItem('fixmate_role_info');
    const storedDisplayName = localStorage.getItem('fixmate_display_name');
    const storedWelcomeMessage = localStorage.getItem('fixmate_welcome_message');
    const storedToken = localStorage.getItem('fixmate_token');
    
    console.log('AuthContext: Stored data found:', {
      hasUser: !!storedUser,
      hasToken: !!storedToken,
      hasRoleInfo: !!storedRoleInfo
    });
    
    if (storedUser && storedToken) {
      const userData = JSON.parse(storedUser);
      console.log('AuthContext: Restoring user session:', userData);
      setUser(userData);
      setRoleInfo(storedRoleInfo ? JSON.parse(storedRoleInfo) : null);
      setDisplayName(storedDisplayName || '');
      setWelcomeMessage(storedWelcomeMessage || '');
      setToken(storedToken);
    }
    setLoading(false);
  }, []);

  const login = async (phone, password = null, name = null, email = null) => {
    try {
      console.log('🔍 LOGIN ATTEMPT:', {
        phone,
        hasPassword: !!password,
        apiBaseUrl: API_BASE,
        environment: process.env.NODE_ENV
      });
      
      const loginData = { 
        phone, 
        name: name || `User ${phone}`,
        email: email || ''
      };
      
      if (password) {
        loginData.password = password;
      }
      
      console.log('🔍 Sending login request to:', `${API_BASE}/auth/login`);
      const response = await axios.post(`${API_BASE}/auth/login`, loginData);
      
      console.log('✅ Login response received:', response.status);
      
      const { 
        user: userData, 
        role_info: roleData,
        display_name: displayNameData,
        welcome_message: welcomeData,
        token: userToken,
        requires_password: requiresPassword = false
      } = response.data;
      
      if (requiresPassword) {
        return { 
          success: true, 
          requiresPassword: true, 
          user: userData, 
          message: "Password setup required" 
        };
      }
      
      // Clear any existing session data to prevent conflicts
      localStorage.clear();
      
      setUser(userData);
      setRoleInfo(roleData);
      setDisplayName(displayNameData);
      setWelcomeMessage(welcomeData);
      setToken(userToken);
      
      // Store in localStorage with role-specific keys to prevent conflicts
      const sessionKey = `fixmate_${roleData?.role || 'client'}`;
      localStorage.setItem(`${sessionKey}_user`, JSON.stringify(userData));
      localStorage.setItem(`${sessionKey}_role_info`, JSON.stringify(roleData));
      localStorage.setItem(`${sessionKey}_display_name`, displayNameData);
      localStorage.setItem(`${sessionKey}_welcome_message`, welcomeData);
      localStorage.setItem(`${sessionKey}_token`, userToken);
      
      // Also store in legacy keys for backward compatibility
      localStorage.setItem('fixmate_user', JSON.stringify(userData));
      localStorage.setItem('fixmate_role_info', JSON.stringify(roleData));
      localStorage.setItem('fixmate_display_name', displayNameData);
      localStorage.setItem('fixmate_welcome_message', welcomeData);
      localStorage.setItem('fixmate_token', userToken);
      
      console.log('✅ Login successful for role:', roleData?.role);
      
      return { success: true, user: userData, roleInfo: roleData };
    } catch (error) {
      console.error('❌ LOGIN ERROR:', error);
      console.error('❌ Error details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url,
        method: error.config?.method
      });
      
      const errorMessage = error.response?.data?.detail || 'Login failed';
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    setUser(null);
    setRoleInfo(null);
    setDisplayName('');
    setWelcomeMessage('');
    setToken(null);
    localStorage.removeItem('fixmate_user');
    localStorage.removeItem('fixmate_role_info');
    localStorage.removeItem('fixmate_display_name');
    localStorage.removeItem('fixmate_welcome_message');
    localStorage.removeItem('fixmate_token');
    
    // Clear any cached data to prevent role conflicts
    console.log('AuthContext: User logged out, session cleared');
  };

  const updateUser = async (userData) => {
    try {
      const response = await axios.put(`${API_BASE}/users/${user.id}`, userData);
      const updatedUser = response.data;
      setUser(updatedUser);
      localStorage.setItem('fixmate_user', JSON.stringify(updatedUser));
      return { success: true, user: updatedUser };
    } catch (error) {
      console.error('Update user error:', error);
      return { success: false, error: error.response?.data?.detail || 'Update failed' };
    }
  };

  const hasPermission = (permission) => {
    return roleInfo?.permissions?.[permission] || false;
  };

  const isRole = (role) => {
    return roleInfo?.role === role;
  };

  const getUserRole = () => {
    return roleInfo?.role || 'client';
  };

  const validateUserRole = (expectedRole) => {
    const currentRole = getUserRole();
    return currentRole === expectedRole;
  };

  const clearRoleConflicts = () => {
    // Clear all role-specific storage keys to prevent conflicts
    const roles = ['client', 'fixer', 'admin'];
    roles.forEach(role => {
      const sessionKey = `fixmate_${role}`;
      localStorage.removeItem(`${sessionKey}_user`);
      localStorage.removeItem(`${sessionKey}_role_info`);
      localStorage.removeItem(`${sessionKey}_display_name`);
      localStorage.removeItem(`${sessionKey}_welcome_message`);
      localStorage.removeItem(`${sessionKey}_token`);
    });
    console.log('AuthContext: Role conflicts cleared');
  };

  const value = {
    user,
    roleInfo,
    displayName,
    welcomeMessage,
    token,
    login,
    logout,
    updateUser,
    hasPermission,
    isRole,
    getUserRole,
    isAuthenticated: !!user && !!token,
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};