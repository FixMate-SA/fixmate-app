import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { getApiUrl } from '../../utils/api';
import Logo from '../Common/Logo';
import PasswordResetModal from './PasswordResetModal';
import LanguageSelector from '../Common/LanguageSelector';

const AdminLogin = () => {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPasswordReset, setShowPasswordReset] = useState(false);
  const { login } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (!phone.trim()) {
      setError('Please enter your phone number');
      setLoading(false);
      return;
    }

    if (!password.trim()) {
      setError('Please enter your password');
      setLoading(false);
      return;
    }

    const result = await login(phone, password);
    
    if (result.success) {
      // Verify this is an admin account
      if (result.roleInfo?.role === 'admin') {
        console.log('AdminLogin: Admin login successful, navigating to admin dashboard');
        navigate('/admin/dashboard', { replace: true });
      } else {
        setError(`This phone number is registered as a ${result.roleInfo?.role}. Please use the correct login page.`);
      }
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-pink-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Language Selector */}
        <div className="flex justify-end">
          <LanguageSelector />
        </div>
        
        <div>
          <Logo 
            size="large" 
            variant="login" 
            showText={true}
            className="mb-8"
          />
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Admin Login
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Access admin dashboard to manage the platform
          </p>
          <p className="mt-1 text-center text-xs text-gray-500">
            Enter your administrator credentials to sign in
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleLogin}>
          <div className="space-y-4">
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                Admin Phone Number
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-red-500 focus:border-red-500 focus:z-10 sm:text-sm"
                placeholder="Enter your admin phone number"
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Admin Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-red-500 focus:border-red-500 focus:z-10 sm:text-sm"
                placeholder="Enter your admin password"
              />
            </div>
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center bg-red-50 p-3 rounded-md">
              {error}
            </div>
          )}

          <div className="space-y-3">
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign in as Admin'}
            </button>
          </div>
          
          <div className="text-center space-y-2">
            <p className="text-xs text-gray-500">
              🔒 Admin access is restricted and monitored
            </p>
            <div className="text-xs text-gray-500 space-y-1">
              <p>Are you a client? <Link to="/client-login" className="text-red-600 hover:text-red-500">Login as Client</Link></p>
              <p>Are you a fixer? <Link to="/fixers-login" className="text-red-600 hover:text-red-500">Login as Fixer</Link></p>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AdminLogin;