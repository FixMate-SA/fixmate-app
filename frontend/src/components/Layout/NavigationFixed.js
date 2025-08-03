import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useLanguage } from '../../contexts/LanguageContext';
import { useAuth } from '../../contexts/AuthContext';

const NavigationFixed = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useLanguage();
  const { hasPermission, isRole, getUserRole } = useAuth();

  const userRole = getUserRole();

  // Enhanced navigation handler that ensures navigation works
  const handleNavigation = (path, event) => {
    event.preventDefault();
    event.stopPropagation();
    
    console.log(`Navigation: Attempting to navigate to ${path}`);
    
    // Force navigation using React Router's navigate function
    navigate(path, { replace: false });
    
    // Backup: Also update browser history
    if (window.history && window.history.pushState) {
      window.history.pushState(null, '', path);
    }
  };

  // Generate role-based path
  const getRoleBasedPath = (basePath) => {
    switch (userRole) {
      case 'admin':
        return `/admin${basePath}`;
      case 'fixer':
        return `/fixer${basePath}`;
      case 'client':
      default:
        return `/client${basePath}`;
    }
  };

  // Navigation items matching system requirements document only
  const completeNavItems = [
    // Core Features  
    { 
      path: getRoleBasedPath('/dashboard'), 
      label: t('dashboard', 'Dashboard'), 
      icon: '📊',
      permission: null
    },
    { 
      path: '/fixers', 
      label: t('fixers', 'Fixers'), 
      icon: '🔧',
      permission: null,
      roles: ['client', 'admin'] // Only clients and admins should see fixers list
    },
    { 
      path: getRoleBasedPath('/learning'), 
      label: t('learning', 'Learning'), 
      icon: '🎓',
      permission: null
    },
    { 
      path: getRoleBasedPath('/business-compliance'), 
      label: t('businessCompliance', 'Business Compliance'), 
      icon: '🏢',
      permission: null,
      roles: ['admin'] // Only admins should see business compliance
    },
    { 
      path: getRoleBasedPath('/sms'), 
      label: t('sms', 'SMS Portal'), 
      icon: '📱',
      permission: null,
      roles: ['admin'] // Only admins should see SMS portal
    },
    
    // Business & Admin Features
    { 
      path: getRoleBasedPath('/enterprise'), 
      label: t('enterprise', 'Enterprise'), 
      icon: '🏢',
      roles: ['admin'],
      permission: null
    },
    { 
      path: getRoleBasedPath('/payment'), 
      label: t('payment', 'Payments'), 
      icon: '💳',
      roles: ['fixer', 'admin'],
      permission: null
    },
    { 
      path: '/admin/panel', 
      label: t('admin', 'Admin Panel'), 
      icon: '⚙️',
      roles: ['admin'],
      permission: null
    },
    { 
      path: '/fixer/jobs', 
      label: t('jobs', 'Jobs'), 
      icon: '🔨',
      roles: ['fixer'],
      permission: null
    },
    { 
      path: '/admin/smart-matching', 
      label: t('smartMatching', 'Smart Matching'), 
      icon: '🎯',
      roles: ['admin'],
      permission: null
    },
    { 
      path: '/admin/photo-verification', 
      label: t('photoVerification', 'Photo Verification'), 
      icon: '📸',
      roles: ['admin'],
      permission: null
    },
    
    // User Profile
    { 
      path: getRoleBasedPath('/profile'), 
      label: t('profile', 'Profile'), 
      icon: '👤',
      permission: null
    }
  ];

  // Filter navigation items based on user role
  const getVisibleNavItems = () => {
    return completeNavItems.filter(item => {
      // If no roles specified, show to everyone
      if (!item.roles) return true;
      
      // Check if user's role is in allowed roles
      if (!item.roles.includes(userRole)) return false;
      
      return true;
    });
  };

  const navItems = getVisibleNavItems();

  const isActive = (path) => {
    return location.pathname === path;
  };

  const getRoleBorderColor = (role, isActive) => {
    if (!isActive) return 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300';
    
    switch (role) {
      case 'admin': return 'border-red-500 text-red-600';
      case 'fixer': return 'border-orange-500 text-orange-600';
      case 'client': return 'border-blue-500 text-blue-600';
      default: return 'border-blue-500 text-blue-600';
    }
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex space-x-2 overflow-x-auto">
          {navItems.map((item) => (
            <a
              key={item.path}
              href={item.path}
              onClick={(e) => handleNavigation(item.path, e)}
              className={`flex items-center space-x-2 py-4 px-3 border-b-2 transition-colors whitespace-nowrap cursor-pointer ${
                getRoleBorderColor(userRole, isActive(item.path))
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="font-medium text-sm">{item.label}</span>
              
              {/* Show role indicator for special items */}
              {item.roles && item.roles.length === 1 && item.roles[0] !== 'client' && (
                <span className={`ml-1 px-1 py-0.5 text-xs rounded ${
                  item.roles[0] === 'admin' ? 'bg-red-100 text-red-600' : 
                  item.roles[0] === 'fixer' ? 'bg-orange-100 text-orange-600' : ''
                }`}>
                  {item.roles[0].charAt(0).toUpperCase()}
                </span>
              )}
            </a>
          ))}
        </div>
        
        {/* Role indicator */}
        <div className="py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs text-gray-500">
              <span>Logged in as:</span>
              <span className={`px-2 py-1 rounded-full font-medium ${
                userRole === 'admin' ? 'bg-red-100 text-red-700' :
                userRole === 'fixer' ? 'bg-green-100 text-green-700' :
                'bg-blue-100 text-blue-700'
              }`}>
                {userRole.charAt(0).toUpperCase() + userRole.slice(1)}
              </span>
            </div>
            
            {userRole === 'fixer' && (
              <div className="text-xs text-gray-500">
                <span>🔧 Fixer Dashboard Active</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default NavigationFixed;