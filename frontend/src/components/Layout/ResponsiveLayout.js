import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Header from './Header';
import MobileHeader from './MobileHeader';
import NavigationFixed from './NavigationFixed';
import MobileBottomNav from './MobileBottomNav';
import Footer from './Footer';

const ResponsiveLayout = ({ children }) => {
  const { user } = useAuth();

  if (!user) {
    // No layout for non-authenticated users
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Desktop Header */}
      <div className="hidden md:block">
        <Header />
        <NavigationFixed />
      </div>

      {/* Mobile Header */}
      <div className="md:hidden">
        <MobileHeader />
      </div>

      {/* Main Content */}
      <main className="main-content">
        <div className="container mx-auto px-4 py-6 md:py-8">
          {children}
        </div>
      </main>

      {/* Desktop Footer */}
      <div className="hidden md:block">
        <Footer />
      </div>

      {/* Mobile Bottom Navigation */}
      <div className="md:hidden">
        <MobileBottomNav />
      </div>
    </div>
  );
};

export default ResponsiveLayout;