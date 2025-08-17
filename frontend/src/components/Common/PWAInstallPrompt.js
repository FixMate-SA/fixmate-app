import React, { useState, useEffect } from 'react';

const PWAInstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    // Check if app is already installed
    const checkInstallation = () => {
      // Check if running as PWA
      const isStandaloneMode = window.matchMedia('(display-mode: standalone)').matches ||
                             window.navigator.standalone === true ||
                             document.referrer.includes('android-app://');
      
      setIsStandalone(isStandaloneMode);
      
      // Check if iOS
      const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      setIsIOS(iOS);
      
      // Check if already installed
      if (isStandaloneMode) {
        setIsInstalled(true);
        return;
      }
      
      // Check if user has dismissed prompt recently
      const dismissed = localStorage.getItem('pwa-prompt-dismissed');
      const dismissedTime = dismissed ? parseInt(dismissed) : 0;
      const daysSinceDismiss = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24);
      
      // Show prompt if not dismissed in last 7 days
      if (daysSinceDismiss > 7) {
        setShowPrompt(true);
      }
    };

    checkInstallation();

    // Listen for the beforeinstallprompt event
    const handleBeforeInstallPrompt = (e) => {
      console.log('📱 PWA: Install prompt available');
      e.preventDefault();
      setDeferredPrompt(e);
      
      // Only show if not dismissed recently
      const dismissed = localStorage.getItem('pwa-prompt-dismissed');
      const dismissedTime = dismissed ? parseInt(dismissed) : 0;
      const daysSinceDismiss = (Date.now() - dismissedTime) / (1000 * 60 * 60 * 24);
      
      if (daysSinceDismiss > 7) {
        setShowPrompt(true);
      }
    };

    // Listen for successful installation
    const handleAppInstalled = () => {
      console.log('📱 PWA: App installed successfully');
      setIsInstalled(true);
      setShowPrompt(false);
      setDeferredPrompt(null);
      
      // Track installation
      if (window.gtag) {
        window.gtag('event', 'pwa_install', {
          event_category: 'PWA',
          event_label: 'App Installed'
        });
      }
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) return;

    console.log('📱 PWA: Triggering install prompt');
    
    // Show the install prompt
    const result = await deferredPrompt.prompt();
    console.log('📱 PWA: User choice:', result.outcome);
    
    // Track user choice
    if (window.gtag) {
      window.gtag('event', 'pwa_install_prompt', {
        event_category: 'PWA',
        event_label: result.outcome
      });
    }

    if (result.outcome === 'accepted') {
      setIsInstalled(true);
    }

    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    console.log('📱 PWA: User dismissed install prompt');
    setShowPrompt(false);
    
    // Remember dismissal
    localStorage.setItem('pwa-prompt-dismissed', Date.now().toString());
    
    // Track dismissal
    if (window.gtag) {
      window.gtag('event', 'pwa_install_dismissed', {
        event_category: 'PWA',
        event_label: 'User Dismissed'
      });
    }
  };

  const handleIOSInstructions = () => {
    setShowPrompt(false);
    
    // Show iOS installation instructions
    const modal = document.createElement('div');
    modal.innerHTML = `
      <div style="
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
      ">
        <div style="
          background: white;
          border-radius: 16px;
          padding: 24px;
          max-width: 320px;
          margin: 20px;
          text-align: center;
        ">
          <h3 style="margin: 0 0 16px 0; color: #1f2937;">Install FixMate-SA</h3>
          <p style="margin: 0 0 20px 0; color: #6b7280; line-height: 1.5;">
            To install this app on your iPhone:
          </p>
          <ol style="text-align: left; color: #374151; line-height: 1.6; margin: 0 0 20px 0; padding-left: 20px;">
            <li>Tap the Share button <span style="font-size: 16px;">⬆️</span> in Safari</li>
            <li>Scroll down and tap "Add to Home Screen" <span style="font-size: 16px;">➕</span></li>
            <li>Tap "Add" to confirm</li>
          </ol>
          <button onclick="this.parentElement.parentElement.remove()" style="
            background: #f97316;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
          ">Got it!</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  };

  // Don't show if already installed or running as standalone
  if (isInstalled || isStandalone) {
    return null;
  }

  // Show iOS-specific prompt
  if (isIOS && showPrompt) {
    return (
      <div className="fixed bottom-4 left-4 right-4 bg-white rounded-lg shadow-xl border border-gray-200 p-4 z-50 mx-auto max-w-sm">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">FM</span>
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-semibold text-gray-900 mb-1">
              Install FixMate-SA App
            </h4>
            <p className="text-xs text-gray-600 mb-3">
              Get the full app experience with offline access and faster loading.
            </p>
            <div className="flex space-x-2">
              <button
                onClick={handleIOSInstructions}
                className="bg-orange-500 text-white text-xs font-medium px-3 py-2 rounded-md hover:bg-orange-600 transition-colors"
              >
                📱 Install Guide
              </button>
              <button
                onClick={handleDismiss}
                className="text-gray-500 text-xs font-medium px-3 py-2 rounded-md hover:text-gray-700 transition-colors"
              >
                Later
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Show standard install prompt
  if (deferredPrompt && showPrompt) {
    return (
      <div className="fixed bottom-4 left-4 right-4 bg-white rounded-lg shadow-xl border border-gray-200 p-4 z-50 mx-auto max-w-sm">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-orange-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">FM</span>
            </div>
          </div>
          <div className="flex-1 min-w-0">
            <h4 className="text-sm font-semibold text-gray-900 mb-1">
              Install FixMate-SA App
            </h4>
            <p className="text-xs text-gray-600 mb-3">
              ✨ Get instant access, offline support, and faster performance.
            </p>
            <div className="flex space-x-2">
              <button
                onClick={handleInstall}
                className="bg-orange-500 text-white text-xs font-medium px-3 py-2 rounded-md hover:bg-orange-600 transition-colors flex items-center space-x-1"
              >
                <span>📱</span>
                <span>Install App</span>
              </button>
              <button
                onClick={handleDismiss}
                className="text-gray-500 text-xs font-medium px-3 py-2 rounded-md hover:text-gray-700 transition-colors"
              >
                Later
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default PWAInstallPrompt;