import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { getApiUrl } from '../../utils/api';
import Logo from '../Common/Logo';
import PasswordResetModal from './PasswordResetModal';
import LanguageSelector from '../Common/LanguageSelector';

const ClientLogin = () => {
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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-green-50 py-6 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-6">
        {/* Language Selector */}
        <div className="flex justify-end">
          <LanguageSelector />
        </div>
        
        <div className="text-center">
          <Logo 
            size="large" 
            variant="login" 
            showText={true}
            className="mb-6"
          />
          <h2 className="text-2xl sm:text-3xl font-extrabold text-gray-900">
            Client Login
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Access your client account to create jobs and hire fixers
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Enter your phone number and password to sign in
          </p>
        </div>
        
        <form className="mt-6 space-y-4" onSubmit={handleLogin}>
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
                className="form-input appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base"
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
                className="form-input appearance-none relative block w-full px-4 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-lg focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base"
                placeholder="Enter your password"
              />
            </div>
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center bg-red-50 p-3 rounded-lg">
              {error}
            </div>
          )}

          <div className="space-y-3">
            <button
              type="submit"
              disabled={loading}
              className="btn-mobile group relative w-full flex justify-center py-3 px-4 border border-transparent text-base font-medium rounded-lg text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Signing in...</span>
                </div>
              ) : (
                'Sign in as Client'
              )}
            </button>

            <div className="text-center">
              <button
                type="button"
                onClick={() => setShowPasswordReset(true)}
                className="text-sm text-blue-600 hover:text-blue-500"
              >
                Forgot your password?
              </button>
            </div>
            
            <div className="text-center">
              <span className="text-sm text-gray-600">or</span>
            </div>
            
            <Link
              to="/client-signup"
              className="btn-mobile group relative w-full flex justify-center py-3 px-4 border border-gray-300 text-base font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Don't have an account? Sign up as Client
            </Link>
          </div>
          
          <div className="text-center space-y-3">
            <p className="text-xs text-gray-500">
              🔒 Your account is protected with secure password authentication
            </p>
            <div className="text-xs text-gray-500 space-y-2">
              <p>Are you a fixer? <Link to="/fixers-login" className="text-indigo-600 hover:text-indigo-500 font-medium">Login as Fixer</Link></p>
              <p>Are you an admin? <Link to="/admin-login" className="text-indigo-600 hover:text-indigo-500 font-medium">Login as Admin</Link></p>
            </div>
          </div>
        </form>

        {/* Password Reset Modal */}
        <PasswordResetModal
          isOpen={showPasswordReset}
          onClose={() => setShowPasswordReset(false)}
          userType="client"
        />
      </div>
    </div>
  );
};

export default ClientLogin;