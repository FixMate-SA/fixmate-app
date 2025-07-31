import React from 'react';
import Header from './Header';
import NavigationFixed from './NavigationFixed';
import Footer from './Footer';
import OfflineIndicator from '../Common/OfflineIndicator';

const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      <NavigationFixed />
      <OfflineIndicator />
      <main className="container mx-auto px-4 py-8 flex-grow">
        {children}
      </main>
      <Footer />
    </div>
  );
};

export default Layout;