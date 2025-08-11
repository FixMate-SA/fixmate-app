import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { useNavigate } from 'react-router-dom';
import PasswordResetModal from './PasswordResetModal';
import Logo from '../Common/Logo';
import LanguageSelector from '../Common/LanguageSelector';

const AdminLogin = () => {
  const { t } = useLanguage();
  const [phoneNumber, setPhoneNumber] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPasswordReset, setShowPasswordReset] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!phoneNumber.trim()) {
      setError(t('phoneNumberRequired', 'Phone number is required'));
      return;
    }
    if (!password.trim()) {
      setError(t('passwordRequired', 'Password is required'));
      return;
    }

    setLoading(true);
    setError('');

    try {
      const result = await login(phoneNumber, password);
      if (result && result.success) {
        // Check if user has admin role
        const userRole = result.roleInfo?.role;
        if (userRole !== 'admin') {
          setError(t('wrongLoginPage', `This phone number is registered as a ${userRole}. Please use the correct login page.`));
          setLoading(false);
          return;
        }
        navigate('/admin/dashboard');
        // Force a page reload to ensure auth context is fully updated
        setTimeout(() => window.location.href = '/admin/dashboard', 100);
      } else {
        setError(t('invalidCredentials', 'Invalid phone number or password'));
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(t('loginError', 'An error occurred during login. Please try again.'));
    }

    setLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-600 to-red-800 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-20 w-20 flex justify-center">
            <Logo />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            {t('adminLogin')}
          </h2>
          <p className="mt-2 text-center text-sm text-red-100">
            {t('adminLoginSubtitle', 'Administrative access to FixMate-SA platform')}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-2xl p-8 space-y-6">
          {/* Language Selector */}
          <div className="flex justify-center">
            <LanguageSelector />
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                {t('phoneNumber')}
              </label>
              <div className="mt-1">
                <input
                  id="phone"
                  name="phone"
                  type="tel"
                  required
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-red-500 focus:border-red-500"
                  placeholder={t('enterPhoneNumber', 'Enter your phone number')}
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                {t('password')}
              </label>
              <div className="mt-1">
                <input
                  id="password"
                  name="password"
                  type="password"
                  required
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-red-500 focus:border-red-500"
                  placeholder={t('enterPassword', 'Enter your password')}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <div className="text-sm text-red-600">{error}</div>
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:bg-red-300 disabled:cursor-not-allowed"
              >
                {loading ? t('signingIn', 'Signing in...') : t('signIn')}
              </button>
            </div>

            <div className="text-center space-y-2">
              <button
                type="button"
                onClick={() => setShowPasswordReset(true)}
                className="text-sm text-red-600 hover:text-red-800 underline"
              >
                {t('forgotPassword', 'Forgot your password?')}
              </button>
            </div>
          </form>
        </div>

        <div className="text-center">
          <div className="text-red-100 text-sm space-x-4">
            <a href="/client-login" className="hover:text-white">
              {t('clientLogin')}
            </a>
            <span>•</span>
            <a href="/fixer-login" className="hover:text-white">
              {t('fixerLogin')}
            </a>
          </div>
        </div>
      </div>

      {showPasswordReset && (
        <PasswordResetModal
          isOpen={showPasswordReset}
          onClose={() => setShowPasswordReset(false)}
          userType="admin"
        />
      )}
    </div>
  );
};

export default AdminLogin;