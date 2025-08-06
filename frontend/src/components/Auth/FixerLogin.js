import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { useNavigate } from 'react-router-dom';
import PasswordResetModal from './PasswordResetModal';
import Logo from '../Common/Logo';
import LanguageSelector from '../Common/LanguageSelector';

const FixerLogin = () => {
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
        // Check if user has fixer role
        const userRole = result.roleInfo?.role;
        if (userRole !== 'fixer') {
          setError(t('wrongLoginPage', `This phone number is registered as a ${userRole}. Please use the correct login page.`));
          setLoading(false);
          return;
        }
        navigate('/fixer/dashboard');
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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-orange-600 to-orange-800 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="mx-auto h-20 w-20 flex justify-center">
            <Logo />
          </div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
            {t('fixerLogin')}
          </h2>
          <p className="mt-2 text-center text-sm text-orange-100">
            {t('fixerLoginSubtitle', 'Access your jobs and grow your service business')}
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
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-orange-500 focus:border-orange-500"
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
                  className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md placeholder-gray-400 focus:outline-none focus:ring-orange-500 focus:border-orange-500"
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
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:bg-orange-300 disabled:cursor-not-allowed"
              >
                {loading ? t('signingIn', 'Signing in...') : t('signIn')}
              </button>
            </div>

            <div className="text-center space-y-2">
              <button
                type="button"
                onClick={() => setShowPasswordReset(true)}
                className="text-sm text-orange-600 hover:text-orange-800 underline"
              >
                {t('forgotPassword', 'Forgot your password?')}
              </button>
              
              <div className="text-sm text-gray-600">
                {t('dontHaveAccount', "Don't have an account?")}{' '}
                <a
                  href="/fixer-signup"
                  className="font-medium text-orange-600 hover:text-orange-800"
                >
                  {t('signUpHere', 'Sign up here')}
                </a>
              </div>
            </div>
          </form>
        </div>

        <div className="text-center">
          <div className="text-orange-100 text-sm space-x-4">
            <a href="/client-login" className="hover:text-white">
              {t('clientLogin')}
            </a>
            <span>•</span>
            <a href="/admin-login" className="hover:text-white">
              {t('adminLogin')}
            </a>
          </div>
        </div>
      </div>

      {showPasswordReset && (
        <PasswordResetModal
          isOpen={showPasswordReset}
          onClose={() => setShowPasswordReset(false)}
          userType="fixer"
        />
      )}
    </div>
  );
};

export default FixerLogin;