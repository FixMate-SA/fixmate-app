import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const MobileBottomNav = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { getUserRole, user } = useAuth();

  const userRole = getUserRole();

  // Get role-based navigation items for mobile
  const getMobileNavItems = () => {
    const baseItems = [
      {
        path: `/${userRole}/dashboard`,
        icon: '🏠',
        label: 'Home',
        roles: ['client', 'fixer', 'admin']
      }
    ];

    const roleSpecificItems = {
      client: [
        { path: '/jobs/create', icon: '➕', label: 'Create Job' },
        { path: '/fixers', icon: '🔧', label: 'Fixers' },
        { path: `/client/profile`, icon: '👤', label: 'Profile' }
      ],
      fixer: [
        { path: '/fixer/jobs', icon: '🔨', label: 'Jobs' },
        { path: '/fixer/payment', icon: '💳', label: 'Payments' },
        { path: `/fixer/profile`, icon: '👤', label: 'Profile' }
      ],
      admin: [
        { path: '/admin/panel', icon: '⚙️', label: 'Admin' },
        { path: '/admin/smart-matching', icon: '🎯', label: 'Matching' },
        { path: `/admin/profile`, icon: '👤', label: 'Profile' }
      ]
    };

    return [...baseItems, ...roleSpecificItems[userRole] || []];
  };

  const navItems = getMobileNavItems();

  const isActive = (path) => {
    return location.pathname === path;
  };

  const getRoleColor = (role, isActive = false) => {
    const colors = {
      admin: isActive ? 'text-red-600' : 'text-gray-500',
      fixer: isActive ? 'text-green-600' : 'text-gray-500', 
      client: isActive ? 'text-blue-600' : 'text-gray-500'
    };
    return colors[role] || colors.client;
  };

  // Only show on mobile screens
  if (!user) return null;

  return (
    <>
      {/* Bottom Navigation - Mobile Only */}
      <div className="md:hidden bottom-nav-mobile">
        <div className="flex justify-around items-center max-w-md mx-auto">
          {navItems.map((item) => (
            <button
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`bottom-nav-item ${isActive(item.path) ? 'active' : ''} ${getRoleColor(userRole, isActive(item.path))}`}
            >
              <div className="bottom-nav-icon">{item.icon}</div>
              <span className="text-xs font-medium">{item.label}</span>
            </button>
          ))}
        </div>
      </div>
      
      {/* Add padding to prevent content from being hidden behind bottom nav */}
      <style jsx="true" global="true">{`
        @media (max-width: 768px) {
          .main-content {
            padding-bottom: 80px;
          }
        }
      `}</style>
    </>
  );
};

export default MobileBottomNav;