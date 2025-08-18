import React, { useState, useEffect } from 'react';

const PWAStatus = () => {
  const [isPWA, setIsPWA] = useState(false);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [showPWAInfo, setShowPWAInfo] = useState(false);

  useEffect(() => {
    // Check if running as PWA
    const checkPWAStatus = () => {
      const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                          window.navigator.standalone === true ||
                          document.referrer.includes('android-app://');
      
      setIsInstalled(isStandalone);
      setIsPWA(isStandalone);

      // Check PWA capabilities more thoroughly
      const hasSW = 'serviceWorker' in navigator;
      const hasManifest = document.querySelector('link[rel="manifest"]') !== null;
      const hasCache = 'caches' in window;
      const isSecure = location.protocol === 'https:' || location.hostname === 'localhost';
      
      // Force PWA availability for all capable browsers
      const isPWACapable = hasSW && hasManifest && hasCache && isSecure;
      setIsInstallable(isPWACapable);
      
      // Debug logging for Heroku troubleshooting
      console.log('🔍 PWA Status Check:', {
        isStandalone,
        hasSW,
        hasManifest,
        hasCache,
        isSecure,
        isPWACapable,
        hostname: location.hostname,
        protocol: location.protocol
      });
    };

    checkPWAStatus();

    // Listen for install prompt
    const handleBeforeInstall = (e) => {
      e.preventDefault();
      setIsInstallable(true);
      console.log('📱 PWA: Install prompt available');
    };

    // Listen for successful installation
    const handleInstalled = () => {
      setIsInstalled(true);
      setIsPWA(true);
      console.log('📱 PWA: App installed');
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    window.addEventListener('appinstalled', handleInstalled);

    // Additional check after DOM is fully loaded
    const recheckTimer = setTimeout(checkPWAStatus, 2000);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
      window.removeEventListener('appinstalled', handleInstalled);
      clearTimeout(recheckTimer);
    };
  }, []);

  // Don't show anything if already installed
  if (isInstalled || isPWA) {
    return (
      <div className="fixed bottom-4 right-4 bg-green-100 text-green-800 text-xs px-3 py-2 rounded-full shadow-lg z-40 flex items-center space-x-2">
        <span className="text-green-600">✅</span>
        <span>PWA Active</span>
      </div>
    );
  }

  // Show PWA availability indicator
  if (isInstallable) {
    return (
      <div className="fixed bottom-4 right-4 z-40">
        <button
          onClick={() => setShowPWAInfo(!showPWAInfo)}
          className="bg-orange-500 text-white text-xs px-3 py-2 rounded-full shadow-lg hover:bg-orange-600 transition-colors flex items-center space-x-2"
        >
          <span>📱</span>
          <span>App Available</span>
        </button>
        
        {showPWAInfo && (
          <div className="absolute bottom-12 right-0 bg-white rounded-lg shadow-xl border border-gray-200 p-4 w-72 z-50">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">FM</span>
                </div>
              </div>
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-gray-900 mb-2">
                  FixMate-SA Progressive Web App
                </h4>
                <p className="text-xs text-gray-600 mb-3">
                  Install for faster performance, offline access, and app-like experience!
                </p>
                
                <div className="space-y-2 mb-3">
                  <div className="flex items-center text-xs text-gray-600">
                    <span className="text-green-500 mr-2">✅</span>
                    <span>Offline Support</span>
                  </div>
                  <div className="flex items-center text-xs text-gray-600">
                    <span className="text-green-500 mr-2">✅</span>
                    <span>Push Notifications</span>
                  </div>
                  <div className="flex items-center text-xs text-gray-600">
                    <span className="text-green-500 mr-2">✅</span>
                    <span>Home Screen Icon</span>
                  </div>
                  <div className="flex items-center text-xs text-gray-600">
                    <span className="text-green-500 mr-2">✅</span>
                    <span>Faster Loading</span>
                  </div>
                </div>
                
                <div className="border-t pt-3">
                  <h5 className="text-xs font-semibold text-gray-800 mb-2">How to Install:</h5>
                  
                  {/* Android/Desktop Instructions */}
                  <div className="mb-2">
                    <p className="text-xs text-gray-600 mb-1">
                      <strong>Chrome/Edge:</strong>
                    </p>
                    <p className="text-xs text-gray-500">
                      Look for "Install" icon in address bar or use browser menu
                    </p>
                  </div>
                  
                  {/* iOS Instructions */}
                  <div className="mb-3">
                    <p className="text-xs text-gray-600 mb-1">
                      <strong>Safari (iOS):</strong>
                    </p>
                    <p className="text-xs text-gray-500">
                      Tap Share ⬆️ → "Add to Home Screen"
                    </p>
                  </div>
                </div>
                
                <div className="flex justify-between">
                  <button
                    onClick={() => setShowPWAInfo(false)}
                    className="text-xs text-gray-500 hover:text-gray-700"
                  >
                    Close
                  </button>
                  <a
                    href="/manifest.json"
                    target="_blank"
                    className="text-xs text-orange-500 hover:text-orange-600"
                  >
                    View Manifest
                  </a>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return null;
};

export default PWAStatus;