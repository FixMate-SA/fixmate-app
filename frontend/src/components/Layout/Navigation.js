import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useLanguage } from '../../contexts/LanguageContext';
import { useAuth } from '../../contexts/AuthContext';

const Navigation = () => {
  const location = useLocation();
  const { t } = useLanguage();
  const { hasPermission, isRole, getUserRole } = useAuth();

  const userRole = getUserRole();

  // Base navigation items available to all users
  const baseNavItems = [
    { 
      path: '/', 
      label: t('dashboard', 'Dashboard'), 
      icon: '📊',
      permission: null // Available to all
    },
  ];

  // Role-specific navigation items
  const roleBasedNavItems = [
    // Jobs available to clients and fixers
    { 
      path: '/jobs', 
      label: t('jobs', 'Jobs'), 
      icon: '🔧',
      roles: ['client', 'fixer', 'admin'],
      permission: 'can_view_jobs'
    },
    
    // Enhanced job creation for clients
    { 
      path: '/jobs/create-workflow', 
      label: t('createJobWorkflow', 'Create Job (Enhanced)'), 
      icon: '✨',
      roles: ['client'],
      permission: 'can_create_jobs'
    },
    
    // Fixer job board
    { 
      path: '/fixer/jobs', 
      label: t('availableJobs', 'Available Jobs'), 
      icon: '🎯',
      roles: ['fixer'],
      permission: 'can_view_jobs'
    },
    { 
      path: '/fixers', 
      label: t('fixers', 'Fixers'), 
      icon: '🔧',
      roles: ['client', 'fixer', 'admin'],
      permission: 'can_view_fixers'
    },
    
    // Learning available to all
    { 
      path: '/learning', 
      label: t('learning', 'Learning'), 
      icon: '🎓',
      roles: ['client', 'fixer', 'admin'],
      permission: 'can_access_learning'
    },
    
    // Business Compliance available to clients and fixers
    { 
      path: '/business-compliance', 
      label: t('businessCompliance', 'Business Compliance'), 
      icon: '🏢',
      roles: ['client', 'fixer', 'admin'],
      permission: null // Remove permission check to always show for all roles
    },
    
    // SMS available to all
    { 
      path: '/sms', 
      label: t('smsPortal', 'SMS Portal'), 
      icon: '📱',
      roles: ['client', 'fixer', 'admin'],
      permission: 'can_access_sms'
    },
    
    // Enterprise features
    { 
      path: '/enterprise', 
      label: t('enterprise', 'Enterprise'), 
      icon: '🏢',
      roles: ['admin'],
      permission: 'can_access_admin'
    },
    
    // Payment management (Fixers and Admins)
    { 
      path: '/payment', 
      label: t('payments', 'Payments'), 
      icon: '💳',
      roles: ['fixer', 'admin'],
      permission: 'can_access_payments'
    },
    
    // Admin Dashboard
    { 
      path: '/admin', 
      label: t('adminPanel', 'Admin Panel'), 
      icon: '⚙️',
      roles: ['admin'],
      permission: null // Remove permission check
    },
    
    // Smart Matching Dashboard (Admin Only)
    { 
      path: '/admin/smart-matching', 
      label: t('smartMatching', 'Smart Matching'), 
      icon: '🎯',
      roles: ['admin'],
      permission: null // Remove permission check
    },
    
    // Photo Verification Dashboard (Admin Only)
    { 
      path: '/admin/photo-verification', 
      label: t('photoVerification', 'Photo Verification'), 
      icon: '📸',
      roles: ['admin'],
      permission: null // Remove permission check
    },
    
    // Phase 3: Automation & Engagement
    { 
      path: '/phase3', 
      label: t('phase3Dashboard', 'Phase 3: Auto & Engage'), 
      icon: '🚀',
      roles: ['client', 'fixer', 'admin'],
      permission: null
    },
    
    // Phase 4: PWA Status Dashboard
    { 
      path: '/pwa-status', 
      label: t('pwaStatus', 'PWA Status'), 
      icon: '📱',
      roles: ['client', 'fixer', 'admin'],
      permission: null
    },
    
    // Phase 4: Performance Dashboard
    { 
      path: '/performance', 
      label: t('performanceDashboard', 'Performance'), 
      icon: '⚡',
      roles: ['client', 'fixer', 'admin'],
      permission: null
    },
    
    // Profile - available to all
    { 
      path: '/profile', 
      label: t('profile', 'Profile'), 
      icon: '👤',
      roles: ['client', 'fixer', 'admin'],
      permission: 'can_manage_profile'
    },
  ];

  // Filter navigation items based on user role and permissions
  const getVisibleNavItems = () => {
    const allItems = [...baseNavItems, ...roleBasedNavItems];
    
    return allItems.filter(item => {
      // If no roles specified, show to everyone
      if (!item.roles) return true;
      
      // Check if user's role is in allowed roles
      if (!item.roles.includes(userRole)) return false;
      
      // For admin users, show all admin items regardless of permission checks
      if (userRole === 'admin' && item.roles.includes('admin')) {
        return true;
      }
      
      // Check permission if specified
      if (item.permission) {
        return hasPermission(item.permission);
      }
      
      return true;
    });
  };

  const navItems = getVisibleNavItems();
  
  // Debug logging to see what items are being filtered
  console.log('Navigation Debug:', {
    userRole: userRole,
    totalBaseItems: baseNavItems.length,
    totalRoleBasedItems: roleBasedNavItems.length,
    filteredItems: navItems.length,
    itemTitles: navItems.map(item => item.label)
  });

  const isActive = (path) => {
    return location.pathname === path;
  };

  // Role-specific styling
  const getRoleBorderColor = (role, isActive) => {
    if (!isActive) return 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300';
    
    switch (role) {
      case 'admin': return 'border-red-500 text-red-600';
      case 'fixer': return 'border-green-500 text-green-600';
      case 'client': return 'border-blue-500 text-blue-600';
      default: return 'border-blue-500 text-blue-600';
    }
  };

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="container mx-auto px-4">
        <div className="flex space-x-2 overflow-x-auto">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-2 py-4 px-3 border-b-2 transition-colors whitespace-nowrap ${
                getRoleBorderColor(userRole, isActive(item.path))
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="font-medium text-sm">{item.label}</span>
              
              {/* Show role indicator for special items */}
              {item.roles && item.roles.length === 1 && item.roles[0] !== 'client' && (
                <span className={`ml-1 px-1 py-0.5 text-xs rounded ${
                  item.roles[0] === 'admin' ? 'bg-red-100 text-red-600' : 
                  item.roles[0] === 'fixer' ? 'bg-green-100 text-green-600' : ''
                }`}>
                  {item.roles[0].charAt(0).toUpperCase()}
                </span>
              )}
            </Link>
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
            
            {userRole === 'admin' && (
              <div className="text-xs text-red-600">
                <span>⚠️ Admin Access Enabled</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;