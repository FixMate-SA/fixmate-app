import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import Logo from '../Common/Logo';
import EmergencyButton from '../Common/EmergencyButton';

const MobileHeader = () => {
  const { user, displayName, logout, getUserRole } = useAuth();
  const [showMenu, setShowMenu] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/client-login');
    setShowMenu(false);
  };

  const userRole = getUserRole();

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-red-600';
      case 'fixer': return 'bg-orange-600';
      case 'client': return 'bg-blue-600';
      default: return 'bg-blue-600';
    }
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-700';
      case 'fixer': return 'bg-orange-100 text-orange-700';
      case 'client': return 'bg-blue-100 text-blue-700';
      default: return 'bg-blue-100 text-blue-700';
    }
  };

  if (!user) return null;

  return (
    <header className={`${getRoleColor(userRole)} text-white shadow-lg relative z-40`}>
      <div className="px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-3">
            <Logo size="small" variant="header" showText={false} />
            <div className="flex flex-col">
              <h1 className="text-lg font-bold">FixMate-SA</h1>
              <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getRoleBadgeColor(userRole)}`}>
                {userRole.charAt(0).toUpperCase() + userRole.slice(1)}
              </span>
            </div>
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center space-x-2">
            {/* Emergency Button */}
            <EmergencyButton size="small" />
            
            {/* Menu Toggle */}
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-2 rounded-md hover:bg-black hover:bg-opacity-20 transition-colors"
              aria-label="Toggle menu"
            >
              <div className="w-6 h-6 flex flex-col justify-around">
                <span className={`block h-0.5 w-6 bg-current transform transition duration-300 ease-in-out ${showMenu ? 'rotate-45 translate-y-1.5' : ''}`}></span>
                <span className={`block h-0.5 w-6 bg-current transition duration-300 ease-in-out ${showMenu ? 'opacity-0' : ''}`}></span>
                <span className={`block h-0.5 w-6 bg-current transform transition duration-300 ease-in-out ${showMenu ? '-rotate-45 -translate-y-1.5' : ''}`}></span>
              </div>
            </button>
          </div>
        </div>

        {/* Welcome Message - Mobile Optimized */}
        <div className="mt-2 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className={`w-8 h-8 ${getRoleColor(userRole)} bg-opacity-80 rounded-full flex items-center justify-center border-2 border-white border-opacity-30`}>
              <span className="text-white font-semibold text-sm">
                {user.display_name ? user.display_name.charAt(0).toUpperCase() : 
                 user.first_name ? user.first_name.charAt(0).toUpperCase() : 'U'}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {displayName || user.full_name || user.display_name || `${user.first_name} ${user.last_name}`}
              </p>
              <p className="text-xs opacity-75">
                Welcome back!
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Dropdown Menu */}
      {showMenu && (
        <div className="absolute top-full left-0 right-0 bg-white shadow-lg border-t z-50">
          <div className="py-2">
            {/* Quick Actions */}
            <div className="px-4 py-2 border-b border-gray-200">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Quick Actions</h3>
              <div className="space-y-1">
                {userRole === 'client' && (
                  <button
                    onClick={() => {
                      navigate('/jobs/create');
                      setShowMenu(false);
                    }}
                    className="flex items-center space-x-3 w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                  >
                    <span>➕</span>
                    <span>Create New Job</span>
                  </button>
                )}
                {userRole === 'fixer' && (
                  <button
                    onClick={() => {
                      navigate('/fixer/jobs');
                      setShowMenu(false);
                    }}
                    className="flex items-center space-x-3 w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                  >
                    <span>🔨</span>
                    <span>View Available Jobs</span>
                  </button>
                )}
                {userRole === 'admin' && (
                  <button
                    onClick={() => {
                      navigate('/admin/panel');
                      setShowMenu(false);
                    }}
                    className="flex items-center space-x-3 w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                  >
                    <span>⚙️</span>
                    <span>Admin Dashboard</span>
                  </button>
                )}
              </div>
            </div>

            {/* Settings */}
            <div className="px-4 py-2 border-b border-gray-200">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Settings</h3>
              <div className="space-y-1">
                <button
                  onClick={() => {
                    navigate(`/${userRole}/profile`);
                    setShowMenu(false);
                  }}
                  className="flex items-center space-x-3 w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                >
                  <span>👤</span>
                  <span>My Profile</span>
                </button>
                <button
                  onClick={() => {
                    navigate(`/${userRole}/learning`);
                    setShowMenu(false);
                  }}
                  className="flex items-center space-x-3 w-full px-3 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 rounded-md"
                >
                  <span>🎓</span>
                  <span>Learning Center</span>
                </button>
              </div>
            </div>

            {/* Logout */}
            <div className="px-4 py-2">
              <button
                onClick={handleLogout}
                className="flex items-center space-x-3 w-full px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 rounded-md"
              >
                <span>🚪</span>
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Overlay to close menu when clicking outside */}
      {showMenu && (
        <div
          className="fixed inset-0 bg-black bg-opacity-25 z-40"
          onClick={() => setShowMenu(false)}
        ></div>
      )}
    </header>
  );
};

export default MobileHeader;