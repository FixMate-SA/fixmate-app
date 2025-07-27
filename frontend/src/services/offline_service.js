class OfflineService {
  constructor() {
    this.isOnline = navigator.onLine;
    this.offlineQueue = [];
    this.setupEventListeners();
    this.initializeOfflineStorage();
  }

  setupEventListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      this.processOfflineQueue();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      this.showOfflineNotification();
    });
  }

  initializeOfflineStorage() {
    // Initialize IndexedDB for offline storage
    this.dbName = 'FixMateOfflineDB';
    this.dbVersion = 1;
    this.db = null;

    const request = indexedDB.open(this.dbName, this.dbVersion);
    
    request.onerror = (event) => {
      console.error('IndexedDB error:', event.target.error);
    };

    request.onsuccess = (event) => {
      this.db = event.target.result;
    };

    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      
      // Create object stores
      if (!db.objectStoreNames.contains('jobs')) {
        db.createObjectStore('jobs', { keyPath: 'id', autoIncrement: true });
      }
      
      if (!db.objectStoreNames.contains('fixers')) {
        db.createObjectStore('fixers', { keyPath: 'id' });
      }
      
      if (!db.objectStoreNames.contains('users')) {
        db.createObjectStore('users', { keyPath: 'id' });
      }
      
      if (!db.objectStoreNames.contains('offlineQueue')) {
        db.createObjectStore('offlineQueue', { keyPath: 'id', autoIncrement: true });
      }
    };
  }

  async storeOfflineData(storeName, data) {
    if (!this.db) return false;

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(data);

      request.onsuccess = () => resolve(true);
      request.onerror = () => reject(request.error);
    });
  }

  async getOfflineData(storeName, key = null) {
    if (!this.db) return null;

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = key ? store.get(key) : store.getAll();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async queueOfflineAction(action) {
    const queueItem = {
      action: action.type,
      data: action.data,
      timestamp: Date.now(),
      retryCount: 0
    };

    this.offlineQueue.push(queueItem);
    await this.storeOfflineData('offlineQueue', queueItem);
    
    return queueItem;
  }

  async processOfflineQueue() {
    if (!this.isOnline || this.offlineQueue.length === 0) return;

    const queueItems = await this.getOfflineData('offlineQueue');
    
    for (const item of queueItems) {
      try {
        await this.processQueueItem(item);
        await this.removeFromQueue(item.id);
      } catch (error) {
        console.error('Error processing queue item:', error);
        item.retryCount++;
        
        if (item.retryCount < 3) {
          await this.storeOfflineData('offlineQueue', item);
        } else {
          await this.removeFromQueue(item.id);
        }
      }
    }
  }

  async processQueueItem(item) {
    const { action, data } = item;
    
    switch (action) {
      case 'CREATE_JOB':
        return await this.syncCreateJob(data);
      case 'UPDATE_JOB':
        return await this.syncUpdateJob(data);
      case 'CREATE_REVIEW':
        return await this.syncCreateReview(data);
      case 'UPDATE_PROFILE':
        return await this.syncUpdateProfile(data);
      default:
        console.warn('Unknown queue action:', action);
    }
  }

  async syncCreateJob(jobData) {
    const response = await fetch('/api/jobs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jobData)
    });

    if (!response.ok) {
      throw new Error('Failed to sync job creation');
    }

    return response.json();
  }

  async syncUpdateJob(jobData) {
    const response = await fetch(`/api/jobs/${jobData.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(jobData)
    });

    if (!response.ok) {
      throw new Error('Failed to sync job update');
    }

    return response.json();
  }

  async syncCreateReview(reviewData) {
    const response = await fetch('/api/reviews', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(reviewData)
    });

    if (!response.ok) {
      throw new Error('Failed to sync review creation');
    }

    return response.json();
  }

  async syncUpdateProfile(profileData) {
    const response = await fetch(`/api/users/${profileData.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData)
    });

    if (!response.ok) {
      throw new Error('Failed to sync profile update');
    }

    return response.json();
  }

  async removeFromQueue(id) {
    if (!this.db) return;

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(['offlineQueue'], 'readwrite');
      const store = transaction.objectStore('offlineQueue');
      const request = store.delete(id);

      request.onsuccess = () => resolve(true);
      request.onerror = () => reject(request.error);
    });
  }

  showOfflineNotification() {
    // Show user-friendly offline notification
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-yellow-500 text-white px-4 py-2 rounded-md shadow-lg z-50';
    notification.innerHTML = `
      <div class="flex items-center space-x-2">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
        </svg>
        <span>You're offline. Changes will sync when reconnected.</span>
      </div>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 5000);
  }

  // API wrapper for offline support
  async apiRequest(url, options = {}) {
    if (this.isOnline) {
      try {
        const response = await fetch(url, options);
        return response;
      } catch (error) {
        if (!navigator.onLine) {
          this.isOnline = false;
          return this.handleOfflineRequest(url, options);
        }
        throw error;
      }
    } else {
      return this.handleOfflineRequest(url, options);
    }
  }

  async handleOfflineRequest(url, options) {
    // Queue the request for later processing
    const action = this.determineActionFromRequest(url, options);
    
    if (action) {
      await this.queueOfflineAction(action);
      
      // Return a mock response for immediate UI feedback
      return {
        ok: true,
        json: async () => ({ 
          success: true, 
          offline: true,
          message: 'Request saved. Will sync when online.' 
        })
      };
    }

    throw new Error('Cannot process request offline');
  }

  determineActionFromRequest(url, options) {
    const method = options.method || 'GET';
    
    if (url.includes('/api/jobs') && method === 'POST') {
      return {
        type: 'CREATE_JOB',
        data: JSON.parse(options.body || '{}')
      };
    }
    
    if (url.includes('/api/jobs') && method === 'PUT') {
      return {
        type: 'UPDATE_JOB',
        data: JSON.parse(options.body || '{}')
      };
    }
    
    if (url.includes('/api/reviews') && method === 'POST') {
      return {
        type: 'CREATE_REVIEW',
        data: JSON.parse(options.body || '{}')
      };
    }
    
    if (url.includes('/api/users') && method === 'PUT') {
      return {
        type: 'UPDATE_PROFILE',
        data: JSON.parse(options.body || '{}')
      };
    }
    
    return null;
  }

  // Cache management
  async cacheResource(key, data) {
    await this.storeOfflineData('cache', { key, data, timestamp: Date.now() });
  }

  async getCachedResource(key) {
    const cached = await this.getOfflineData('cache', key);
    
    if (cached) {
      // Check if cache is still valid (24 hours)
      const isValid = Date.now() - cached.timestamp < 24 * 60 * 60 * 1000;
      
      if (isValid) {
        return cached.data;
      }
    }
    
    return null;
  }

  getConnectionStatus() {
    return {
      isOnline: this.isOnline,
      queueLength: this.offlineQueue.length,
      lastSync: localStorage.getItem('fixmate_last_sync') || 'Never'
    };
  }
}

export default new OfflineService();