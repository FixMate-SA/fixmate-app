import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Header from './Header';
import CleanMobileHeader from './CleanMobileHeader';
import MobileResponsiveNav from './MobileResponsiveNav';
import NavigationFixed from './NavigationFixed';
import MobileBottomNav from './MobileBottomNav';
import Footer from './Footer';
import PWAStatus from '../Common/PWAStatus';

const ProfessionalLayout = ({ children }) => {
  const { user } = useAuth();

  if (!user) {
    // No layout for non-authenticated users
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Desktop Header */}
      <div className="hidden lg:block">
        <Header />
        <NavigationFixed />
      </div>

      {/* Mobile/Tablet Header */}
      <div className="lg:hidden">
        <CleanMobileHeader />
        <MobileResponsiveNav />
      </div>

      {/* Main Content */}
      <main className="main-content">
        <div className="container mx-auto px-4 py-6 lg:py-8">
          {children}
        </div>
      </main>

      {/* Desktop Footer */}
      <div className="hidden lg:block">
        <Footer />
      </div>

      {/* Mobile Bottom Navigation */}
      <div className="lg:hidden">
        <MobileBottomNav />
      </div>

      {/* PWA Components for authenticated users */}
      <PWAStatus />
    </div>
  );
};

export default ProfessionalLayout;