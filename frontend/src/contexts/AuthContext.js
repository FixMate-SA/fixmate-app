import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

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

  const API_BASE = `${process.env.REACT_APP_BACKEND_URL}/api`;

  useEffect(() => {
    // Check for stored auth data on app load
    const storedUser = localStorage.getItem('fixmate_user');
    const storedRoleInfo = localStorage.getItem('fixmate_role_info');
    const storedDisplayName = localStorage.getItem('fixmate_display_name');
    const storedWelcomeMessage = localStorage.getItem('fixmate_welcome_message');
    const storedToken = localStorage.getItem('fixmate_token');
    
    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
      setRoleInfo(storedRoleInfo ? JSON.parse(storedRoleInfo) : null);
      setDisplayName(storedDisplayName || '');
      setWelcomeMessage(storedWelcomeMessage || '');
      setToken(storedToken);
    }
    setLoading(false);
  }, []);

  const login = async (phone, name = null, email = null) => {
    try {
      const response = await axios.post(`${API_BASE}/auth/login`, { 
        phone, 
        name: name || `User ${phone}`,
        email: email || ''
      });
      
      const { 
        user: userData, 
        role_info: roleData,
        display_name: displayNameData,
        welcome_message: welcomeData,
        token: userToken 
      } = response.data;
      
      setUser(userData);
      setRoleInfo(roleData);
      setDisplayName(displayNameData);
      setWelcomeMessage(welcomeData);
      setToken(userToken);
      
      // Store in localStorage
      localStorage.setItem('fixmate_user', JSON.stringify(userData));
      localStorage.setItem('fixmate_role_info', JSON.stringify(roleData));
      localStorage.setItem('fixmate_display_name', displayNameData);
      localStorage.setItem('fixmate_welcome_message', welcomeData);
      localStorage.setItem('fixmate_token', userToken);
      
      return { success: true, user: userData, roleInfo: roleData };
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
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