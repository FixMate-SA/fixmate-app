// PWA Service Manager - Handles service worker registration and PWA features
class PWAService {
  constructor() {
    this.swRegistration = null;
    this.isOnline = navigator.onLine;
    this.installPrompt = null;
    this.notificationPermission = 'default';
    
    this.init();
  }

  async init() {
    try {
      // Register service worker
      await this.registerServiceWorker();
      
      // Setup PWA features
      this.setupInstallPrompt();
      this.setupNetworkListener();
      this.setupNotifications();
      
      console.log('PWA Service: Initialized successfully');
    } catch (error) {
      console.error('PWA Service: Initialization failed', error);
    }
  }

  // Register service worker
  async registerServiceWorker() {
    if ('serviceWorker' in navigator) {
      try {
        this.swRegistration = await navigator.serviceWorker.register('/sw.js', {
          scope: '/'
        });

        console.log('PWA Service: Service Worker registered successfully');

        // Handle updates
        this.swRegistration.addEventListener('updatefound', () => {
          const newWorker = this.swRegistration.installing;
          
          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              this.showUpdateNotification();
            }
          });
        });

        // Listen for messages from service worker
        navigator.serviceWorker.addEventListener('message', this.handleServiceWorkerMessage.bind(this));

        return this.swRegistration;
      } catch (error) {
        console.error('PWA Service: Service Worker registration failed', error);
        throw error;
      }
    } else {
      throw new Error('Service Workers not supported');
    }
  }

  // Handle messages from service worker
  handleServiceWorkerMessage(event) {
    const { type, payload } = event.data;
    
    switch (type) {
      case 'CACHE_UPDATED':
        console.log('PWA Service: Cache updated', payload);
        this.notifyUser('App updated successfully!', 'success');
        break;
      case 'SYNC_COMPLETE':
        console.log('PWA Service: Background sync completed', payload);
        this.notifyUser('Data synced successfully!', 'success');
        break;
      case 'OFFLINE_ACTION_QUEUED':
        console.log('PWA Service: Action queued for when online', payload);
        this.notifyUser('Action saved. Will sync when online.', 'info');
        break;
      default:
        console.log('PWA Service: Unknown message from SW', event.data);
    }
  }

  // Setup app installation prompt
  setupInstallPrompt() {
    window.addEventListener('beforeinstallprompt', (event) => {
      event.preventDefault();
      this.installPrompt = event;
      this.showInstallBanner();
    });

    // Handle app installed
    window.addEventListener('appinstalled', () => {
      console.log('PWA Service: App installed successfully');
      this.hideInstallBanner();
      this.notifyUser('FixMate-SA installed successfully!', 'success');
    });
  }

  // Show install banner
  showInstallBanner() {
    // Create install banner if it doesn't exist
    if (!document.getElementById('pwa-install-banner')) {
      const banner = document.createElement('div');
      banner.id = 'pwa-install-banner';
      banner.className = 'fixed bottom-4 left-4 right-4 bg-blue-600 text-white p-4 rounded-lg shadow-lg z-50 flex items-center justify-between';
      banner.innerHTML = `
        <div class="flex items-center">
          <div class="text-2xl mr-3">📱</div>
          <div>
            <div class="font-semibold">Install FixMate-SA</div>
            <div class="text-sm opacity-90">Get the full app experience</div>
          </div>
        </div>
        <div class="flex space-x-2">
          <button id="pwa-install-btn" class="bg-white text-blue-600 px-3 py-1 rounded font-medium">Install</button>
          <button id="pwa-dismiss-btn" class="text-white opacity-75 hover:opacity-100">✕</button>
        </div>
      `;

      document.body.appendChild(banner);

      // Add event listeners
      document.getElementById('pwa-install-btn').addEventListener('click', () => {
        this.promptInstall();
      });

      document.getElementById('pwa-dismiss-btn').addEventListener('click', () => {
        this.hideInstallBanner();
      });
    }
  }

  // Hide install banner
  hideInstallBanner() {
    const banner = document.getElementById('pwa-install-banner');
    if (banner) {
      banner.remove();
    }
  }

  // Prompt app installation
  async promptInstall() {
    if (this.installPrompt) {
      this.installPrompt.prompt();
      const result = await this.installPrompt.userChoice;
      
      if (result.outcome === 'accepted') {
        console.log('PWA Service: User accepted install prompt');
      } else {
        console.log('PWA Service: User dismissed install prompt');
      }
      
      this.installPrompt = null;
      this.hideInstallBanner();
    }
  }

  // Setup network status listener
  setupNetworkListener() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      console.log('PWA Service: Back online');
      this.notifyUser('Connection restored!', 'success');
      this.syncOfflineActions();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      console.log('PWA Service: Gone offline');
      this.notifyUser('You are now offline. Some features may be limited.', 'warning');
    });
  }

  // Setup push notifications
  async setupNotifications() {
    if ('Notification' in window && 'serviceWorker' in navigator) {
      this.notificationPermission = Notification.permission;
      
      if (this.notificationPermission === 'default') {
        // Show notification permission request after user interaction
        this.showNotificationPermissionPrompt();
      }
    }
  }

  // Show notification permission prompt
  showNotificationPermissionPrompt() {
    // Create notification prompt if it doesn't exist
    if (!document.getElementById('notification-permission-prompt')) {
      setTimeout(() => {
        const prompt = document.createElement('div');
        prompt.id = 'notification-permission-prompt';
        prompt.className = 'fixed top-4 left-4 right-4 bg-green-600 text-white p-4 rounded-lg shadow-lg z-50 flex items-center justify-between';
        prompt.innerHTML = `
          <div class="flex items-center">
            <div class="text-2xl mr-3">🔔</div>
            <div>
              <div class="font-semibold">Stay Updated</div>
              <div class="text-sm opacity-90">Get notified about job updates and messages</div>
            </div>
          </div>
          <div class="flex space-x-2">
            <button id="enable-notifications-btn" class="bg-white text-green-600 px-3 py-1 rounded font-medium">Enable</button>
            <button id="dismiss-notifications-btn" class="text-white opacity-75 hover:opacity-100">Later</button>
          </div>
        `;

        document.body.appendChild(prompt);

        // Add event listeners
        document.getElementById('enable-notifications-btn').addEventListener('click', () => {
          this.requestNotificationPermission();
          prompt.remove();
        });

        document.getElementById('dismiss-notifications-btn').addEventListener('click', () => {
          prompt.remove();
        });
      }, 5000); // Show after 5 seconds
    }
  }

  // Request notification permission
  async requestNotificationPermission() {
    try {
      const permission = await Notification.requestPermission();
      this.notificationPermission = permission;
      
      if (permission === 'granted') {
        console.log('PWA Service: Notification permission granted');
        this.notifyUser('Notifications enabled successfully!', 'success');
        
        // Subscribe to push notifications
        await this.subscribeToPushNotifications();
      } else {
        console.log('PWA Service: Notification permission denied');
        this.notifyUser('Notifications disabled. You can enable them in settings.', 'info');
      }
    } catch (error) {
      console.error('PWA Service: Failed to request notification permission', error);
    }
  }

  // Subscribe to push notifications
  async subscribeToPushNotifications() {
    try {
      if (this.swRegistration) {
        const subscription = await this.swRegistration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: this.urlB64ToUint8Array(process.env.REACT_APP_VAPID_PUBLIC_KEY || '')
        });

        console.log('PWA Service: Push subscription created', subscription);
        
        // Send subscription to server
        await this.sendSubscriptionToServer(subscription);
      }
    } catch (error) {
      console.error('PWA Service: Failed to subscribe to push notifications', error);
    }
  }

  // Send push subscription to server
  async sendSubscriptionToServer(subscription) {
    try {
      await fetch('/api/push/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`
        },
        body: JSON.stringify(subscription)
      });
      
      console.log('PWA Service: Push subscription sent to server');
    } catch (error) {
      console.error('PWA Service: Failed to send subscription to server', error);
    }
  }

  // Convert VAPID key
  urlB64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/\-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  // Sync offline actions
  async syncOfflineActions() {
    if (this.swRegistration && this.swRegistration.sync) {
      try {
        await this.swRegistration.sync.register('general-sync');
        console.log('PWA Service: Background sync registered');
      } catch (error) {
        console.error('PWA Service: Background sync registration failed', error);
      }
    }
  }

  // Queue action for offline sync
  async queueOfflineAction(action, data) {
    try {
      // Store in IndexedDB or localStorage for sync when online
      const offlineActions = JSON.parse(localStorage.getItem('offline_actions') || '[]');
      
      offlineActions.push({
        id: Date.now().toString(),
        action,
        data,
        timestamp: new Date().toISOString()
      });
      
      localStorage.setItem('offline_actions', JSON.stringify(offlineActions));
      
      // Register background sync
      if (this.swRegistration && this.swRegistration.sync) {
        await this.swRegistration.sync.register(action);
      }
      
      console.log('PWA Service: Action queued for offline sync', action);
      this.notifyUser('Action saved. Will sync when online.', 'info');
    } catch (error) {
      console.error('PWA Service: Failed to queue offline action', error);
    }
  }

  // Get cached data
  async getCachedData(url) {
    try {
      const cache = await caches.open('fixmate-sa-v1.0.0');
      const response = await cache.match(url);
      
      if (response) {
        return await response.json();
      }
      
      return null;
    } catch (error) {
      console.error('PWA Service: Failed to get cached data', error);
      return null;
    }
  }

  // Cache data
  async cacheData(url, data) {
    try {
      const cache = await caches.open('fixmate-sa-v1.0.0');
      const response = new Response(JSON.stringify(data));
      await cache.put(url, response);
      
      console.log('PWA Service: Data cached successfully', url);
    } catch (error) {
      console.error('PWA Service: Failed to cache data', error);
    }
  }

  // Show user notification
  notifyUser(message, type = 'info') {
    // Create notification toast
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 max-w-sm transform translate-x-full transition-transform duration-300 ${
      type === 'success' ? 'bg-green-600 text-white' :
      type === 'error' ? 'bg-red-600 text-white' :
      type === 'warning' ? 'bg-yellow-600 text-white' :
      'bg-blue-600 text-white'
    }`;
    
    toast.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <div class="text-lg mr-2">
            ${type === 'success' ? '✓' : 
              type === 'error' ? '✗' : 
              type === 'warning' ? '⚠' : 'ℹ'}
          </div>
          <div>${message}</div>
        </div>
        <button class="ml-4 text-white opacity-75 hover:opacity-100">✕</button>
      </div>
    `;

    document.body.appendChild(toast);

    // Animate in
    setTimeout(() => {
      toast.style.transform = 'translateX(0)';
    }, 100);

    // Auto remove after 5 seconds
    setTimeout(() => {
      toast.style.transform = 'translate(100%)';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    }, 5000);

    // Add close button functionality
    toast.querySelector('button').addEventListener('click', () => {
      toast.style.transform = 'translateX(100%)';
      setTimeout(() => {
        if (toast.parentNode) {
          toast.parentNode.removeChild(toast);
        }
      }, 300);
    });
  }

  // Show update notification
  showUpdateNotification() {
    const updateBanner = document.createElement('div');
    updateBanner.className = 'fixed top-0 left-0 right-0 bg-blue-600 text-white p-3 z-50 flex items-center justify-between';
    updateBanner.innerHTML = `
      <div class="flex items-center">
        <div class="text-lg mr-3">🔄</div>
        <div>
          <div class="font-semibold">Update Available</div>
          <div class="text-sm opacity-90">A new version of FixMate-SA is ready</div>
        </div>
      </div>
      <div class="flex space-x-2">
        <button id="update-app-btn" class="bg-white text-blue-600 px-3 py-1 rounded font-medium">Update</button>
        <button id="dismiss-update-btn" class="text-white opacity-75 hover:opacity-100">Later</button>
      </div>
    `;

    document.body.appendChild(updateBanner);

    // Add event listeners
    document.getElementById('update-app-btn').addEventListener('click', () => {
      this.activateUpdate();
      updateBanner.remove();
    });

    document.getElementById('dismiss-update-btn').addEventListener('click', () => {
      updateBanner.remove();
    });
  }

  // Activate service worker update
  activateUpdate() {
    if (this.swRegistration && this.swRegistration.waiting) {
      this.swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
      window.location.reload();
    }
  }

  // Get PWA status
  getPWAStatus() {
    return {
      isServiceWorkerSupported: 'serviceWorker' in navigator,
      isServiceWorkerRegistered: !!this.swRegistration,
      isOnline: this.isOnline,
      notificationPermission: this.notificationPermission,
      isInstallable: !!this.installPrompt,
      isInstalled: window.matchMedia && window.matchMedia('(display-mode: standalone)').matches
    };
  }
}

// Export PWA service
export default PWAService;