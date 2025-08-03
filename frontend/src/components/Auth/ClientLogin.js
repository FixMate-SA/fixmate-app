import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { getApiUrl } from '../../utils/api';
import Logo from '../Common/Logo';
import LanguageSelector from '../Common/LanguageSelector';

const ClientLogin = () => {
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
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
      // Verify this is a client account
      if (result.roleInfo?.role === 'client') {
        console.log('ClientLogin: Client login successful, navigating to client dashboard');
        navigate('/client/dashboard', { replace: true });
      } else {
        setError(`This phone number is registered as a ${result.roleInfo?.role}. Please use the correct login page.`);
      }
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-green-50 py-12 px-4 sm:px-6 lg:px-8">
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
            Client Login
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Access your client account to create jobs and hire fixers
          </p>
          <p className="mt-1 text-center text-xs text-gray-500">
            Enter your phone number and password to sign in
          </p>
        </div>
        
        <form className="mt-8 space-y-6" onSubmit={handleLogin}>
          <div className="space-y-4">
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                Phone Number
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Enter your phone number (e.g., +27821234567)"
              />
            </div>
            
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Enter your password"
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
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign in as Client'}
            </button>
            
            <div className="text-center">
              <span className="text-sm text-gray-600">or</span>
            </div>
            
            <Link
              to="/client-signup"
              className="group relative w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Don't have an account? Sign up as Client
            </Link>
          </div>
          
          <div className="text-center space-y-2">
            <p className="text-xs text-gray-500">
              🔒 Your account is protected with secure password authentication
            </p>
            <div className="text-xs text-gray-500 space-y-1">
              <p>Are you a fixer? <Link to="/fixers-login" className="text-indigo-600 hover:text-indigo-500">Login as Fixer</Link></p>
              <p>Are you an admin? <Link to="/admin-login" className="text-indigo-600 hover:text-indigo-500">Login as Admin</Link></p>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ClientLogin;