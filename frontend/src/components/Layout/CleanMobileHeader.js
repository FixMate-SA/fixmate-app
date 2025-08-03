import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import Logo from '../Common/Logo';
import EmergencyButton from '../Common/EmergencyButton';

const CleanMobileHeader = () => {
  const { user, displayName, logout, getUserRole } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/client-login');
  };

  const userRole = getUserRole();

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-red-600';
      case 'fixer': return 'bg-green-600';
      case 'client': return 'bg-blue-600';
      default: return 'bg-blue-600';
    }
  };

  if (!user) return null;

  return (
    <header className={`${getRoleColor(userRole)} text-white shadow-lg`}>
      <div className="px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <Logo size="small" variant="header" showText={false} />
            <div>
              <h1 className="text-xl font-bold">FixMate-SA</h1>
              <div className="flex items-center space-x-2">
                <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-white bg-opacity-20">
                  {userRole.charAt(0).toUpperCase() + userRole.slice(1)}
                </span>
              </div>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-3">
            {/* User Info - Compact */}
            <div className="flex items-center space-x-2">
              <div className={`w-8 h-8 ${getRoleColor(userRole)} bg-opacity-80 rounded-full flex items-center justify-center border-2 border-white border-opacity-30`}>
                <span className="text-white font-semibold text-sm">
                  {user.display_name ? user.display_name.charAt(0).toUpperCase() : 
                   user.first_name ? user.first_name.charAt(0).toUpperCase() : 'U'}
                </span>
              </div>
              <div className="hidden sm:block">
                <p className="text-sm font-medium">
                  {displayName || user.full_name || user.display_name || `${user.first_name} ${user.last_name}`}
                </p>
              </div>
            </div>

            {/* Emergency Button */}
            <EmergencyButton size="small" />

            {/* Logout Button */}
            <button
              onClick={handleLogout}
              className="flex items-center space-x-1 px-3 py-1.5 rounded-md bg-white bg-opacity-20 hover:bg-opacity-30 transition-colors text-sm font-medium"
            >
              <span>🚪</span>
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default CleanMobileHeader;