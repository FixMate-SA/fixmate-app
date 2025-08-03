import React, { useState, useRef, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const MobileResponsiveNav = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { getUserRole } = useAuth();
  const scrollRef = useRef(null);
  const [showLeftArrow, setShowLeftArrow] = useState(false);
  const [showRightArrow, setShowRightArrow] = useState(false);

  const userRole = getUserRole();

  // Core navigation items - much cleaner and focused
  const getNavItems = () => {
    const baseItems = [
      { 
        path: `/${userRole}/dashboard`, 
        label: 'Dashboard',
        icon: '📊',
        priority: 1
      }
    ];

    const roleSpecificItems = {
      client: [
        { path: '/jobs/create', label: 'Create Job', icon: '➕', priority: 2 },
        { path: '/fixers', label: 'Find Fixers', icon: '🔧', priority: 3 },
        { path: '/jobs/list', label: 'My Jobs', icon: '📋', priority: 4 },
        { path: `/${userRole}/learning`, label: 'Learning', icon: '🎓', priority: 5 },
        { path: `/${userRole}/profile`, label: 'Profile', icon: '👤', priority: 6 }
      ],
      fixer: [
        { path: '/fixer/jobs', label: 'Available Jobs', icon: '🔨', priority: 2 },
        { path: '/fixer/payment', label: 'Payments', icon: '💳', priority: 3 },
        { path: `/${userRole}/learning`, label: 'Learning', icon: '🎓', priority: 4 },
        { path: '/fixer/reputation', label: 'Reputation', icon: '⭐', priority: 5 },
        { path: `/${userRole}/profile`, label: 'Profile', icon: '👤', priority: 6 }
      ],
      admin: [
        { path: '/admin/panel', label: 'Admin Panel', icon: '⚙️', priority: 2 },
        { path: '/admin/smart-matching', label: 'Smart Matching', icon: '🎯', priority: 3 },
        { path: '/admin/photo-verification', label: 'Photo Verification', icon: '📸', priority: 4 },
        { path: '/admin/business-compliance', label: 'Business', icon: '🏢', priority: 5 },
        { path: '/admin/enterprise', label: 'Enterprise', icon: '🏭', priority: 6 },
        { path: '/admin/payment', label: 'Payments', icon: '💳', priority: 7 },
        { path: `/${userRole}/learning`, label: 'Learning', icon: '🎓', priority: 8 },
        { path: `/${userRole}/profile`, label: 'Profile', icon: '👤', priority: 9 }
      ]
    };

    return [...baseItems, ...(roleSpecificItems[userRole] || [])];
  };

  const navItems = getNavItems();

  // Check scroll position and update arrow visibility
  const checkScrollPosition = () => {
    if (scrollRef.current) {
      const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
      setShowLeftArrow(scrollLeft > 0);
      setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 1);
    }
  };

  useEffect(() => {
    checkScrollPosition();
    const handleResize = () => checkScrollPosition();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [navItems]);

  const scroll = (direction) => {
    if (scrollRef.current) {
      const scrollAmount = 200;
      const newScrollLeft = scrollRef.current.scrollLeft + (direction === 'left' ? -scrollAmount : scrollAmount);
      scrollRef.current.scrollTo({ left: newScrollLeft, behavior: 'smooth' });
    }
  };

  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  const getRoleColor = (role) => {
    switch (role) {
      case 'admin': return 'border-red-500 bg-red-50';
      case 'fixer': return 'border-green-500 bg-green-50';
      case 'client': return 'border-blue-500 bg-blue-50';
      default: return 'border-blue-500 bg-blue-50';
    }
  };

  const getRoleActiveColor = (role) => {
    switch (role) {
      case 'admin': return 'bg-red-600 text-white border-red-600';
      case 'fixer': return 'bg-green-600 text-white border-green-600';
      case 'client': return 'bg-blue-600 text-white border-blue-600';
      default: return 'bg-blue-600 text-white border-blue-600';
    }
  };

  const getRoleTextColor = (role) => {
    switch (role) {
      case 'admin': return 'text-red-700';
      case 'fixer': return 'text-green-700';
      case 'client': return 'text-blue-700';
      default: return 'text-blue-700';
    }
  };

  return (
    <div className="bg-white border-b border-gray-200 sticky top-0 z-30">
      <div className="relative">
        {/* Left Arrow */}
        {showLeftArrow && (
          <button
            onClick={() => scroll('left')}
            className="absolute left-0 top-0 bottom-0 z-10 bg-white bg-opacity-90 border-r border-gray-200 px-2 flex items-center justify-center hover:bg-gray-50 transition-colors"
            aria-label="Scroll left"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}

        {/* Navigation Items */}
        <div
          ref={scrollRef}
          className="flex overflow-x-auto scrollbar-hide py-3 px-4"
          style={{ 
            scrollbarWidth: 'none',
            msOverflowStyle: 'none',
            paddingLeft: showLeftArrow ? '40px' : '16px',
            paddingRight: showRightArrow ? '40px' : '16px'
          }}
          onScroll={checkScrollPosition}
        >
          <div className="flex space-x-2 min-w-max">
            {navItems.map((item) => (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`
                  flex items-center space-x-2 px-4 py-2 rounded-full border-2 font-medium text-sm whitespace-nowrap transition-all duration-200 min-w-max
                  ${isActive(item.path) 
                    ? getRoleActiveColor(userRole)
                    : `${getRoleColor(userRole)} ${getRoleTextColor(userRole)} hover:bg-opacity-80`
                  }
                `}
              >
                <span className="text-base">{item.icon}</span>
                <span>{item.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Right Arrow */}
        {showRightArrow && (
          <button
            onClick={() => scroll('right')}
            className="absolute right-0 top-0 bottom-0 z-10 bg-white bg-opacity-90 border-l border-gray-200 px-2 flex items-center justify-center hover:bg-gray-50 transition-colors"
            aria-label="Scroll right"
          >
            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}
      </div>

      {/* Hide scrollbar */}
      <style jsx="true">{`
        .scrollbar-hide {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
        .scrollbar-hide::-webkit-scrollbar {
          display: none;
        }
      `}</style>
    </div>
  );
};

export default MobileResponsiveNav;