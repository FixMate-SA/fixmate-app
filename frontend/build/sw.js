// FixMate-SA Progressive Web App Service Worker
// Enhanced with offline support, background sync, and push notifications

const CACHE_NAME = 'fixmate-sa-v2.1.0';
const STATIC_CACHE = 'fixmate-static-v2.1.0';
const DYNAMIC_CACHE = 'fixmate-dynamic-v2.1.0';
const API_CACHE = 'fixmate-api-v2.1.0';

// Resources to cache immediately
const STATIC_ASSETS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/fixmate-logo.jpg',
  '/offline.html',
  // Core app routes
  '/dashboard',
  '/fixers', 
  '/jobs',
  '/create-job',
  '/profile',
  '/business-compliance',
  // Authentication routes
  '/login',
  '/client-login',
  '/fixer-login',
  '/admin-login',
  '/signup',
  '/client-signup',
  '/fixer-signup'
];

// API endpoints to cache
const API_ENDPOINTS = [
  '/api/fixers',
  '/api/jobs',
  '/api/dashboard',
  '/api/auth/me'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('🔧 FixMate-SA Service Worker: Installing...');
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(STATIC_CACHE).then((cache) => {
        console.log('📦 Caching static assets...');
        return cache.addAll(STATIC_ASSETS.map(url => new Request(url, {
          mode: 'no-cors',
          cache: 'reload'
        })));
      }).catch(err => {
        console.warn('⚠️ Some static assets failed to cache:', err);
        // Continue installation even if some assets fail
        return Promise.resolve();
      }),
      
      // Initialize other caches
      caches.open(DYNAMIC_CACHE),
      caches.open(API_CACHE)
    ]).then(() => {
      console.log('✅ FixMate-SA Service Worker: Installation complete');
      // Force activation immediately for better UX
      return self.skipWaiting();
    })
  );
});

// Handle messages from main app
self.addEventListener('message', (event) => {
  console.log('📨 Service Worker received message:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log('⚡ Service Worker: Skipping waiting phase');
    self.skipWaiting();
  }
});

// Activate event - cleanup old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 FixMate-SA Service Worker: Activating...');
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && 
                cacheName !== DYNAMIC_CACHE && 
                cacheName !== API_CACHE &&
                cacheName !== CACHE_NAME) {
              console.log('🗑️ Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Take control of all clients
      self.clients.claim()
    ]).then(() => {
      console.log('✅ FixMate-SA Service Worker: Activation complete');
    })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Handle different types of requests
  if (url.pathname.startsWith('/api/')) {
    // API requests - Network First with cache fallback
    event.respondWith(handleApiRequest(request));
  } else if (STATIC_ASSETS.some(asset => url.pathname === asset || url.pathname.startsWith(asset))) {
    // Static assets - Cache First
    event.respondWith(handleStaticRequest(request));
  } else if (url.pathname.startsWith('/static/')) {
    // Static files (JS, CSS, images) - Cache First
    event.respondWith(handleStaticRequest(request));
  } else {
    // Navigation requests - Network First with offline fallback
    event.respondWith(handleNavigationRequest(request));
  }
});

// API Request Handler - Network First
async function handleApiRequest(request) {
  const url = new URL(request.url);
  
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful API responses
      const cache = await caches.open(API_CACHE);
      
      // Only cache GET requests for certain endpoints
      if (API_ENDPOINTS.some(endpoint => url.pathname.startsWith(endpoint))) {
        cache.put(request, networkResponse.clone());
      }
      
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
  } catch (error) {
    console.log('📡 Network failed for API request, trying cache:', url.pathname);
    
    // Try cache fallback
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return error response
    return new Response(
      JSON.stringify({ 
        success: false, 
        message: 'Offline - Please check your connection',
        cached: false
      }),
      { 
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Static Request Handler - Cache First
async function handleStaticRequest(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('📦 Failed to fetch static asset:', request.url);
    
    // For images, return a placeholder
    if (request.destination === 'image') {
      return new Response(
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="#f3f4f6"/><text x="100" y="100" text-anchor="middle" fill="#6b7280">Image Offline</text></svg>',
        { headers: { 'Content-Type': 'image/svg+xml' }}
      );
    }
    
    throw error;
  }
}

// Navigation Request Handler - Network First with offline page
async function handleNavigationRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      // Cache successful navigation responses
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('🌐 Network failed for navigation, trying cache:', request.url);
    
    // Try cache fallback
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for navigation requests
    const offlinePage = await caches.match('/offline.html');
    if (offlinePage) {
      return offlinePage;
    }
    
    // Final fallback
    return new Response(
      '<!DOCTYPE html><html><head><title>FixMate-SA - Offline</title></head><body><h1>You are offline</h1><p>Please check your internet connection and try again.</p></body></html>',
      { headers: { 'Content-Type': 'text/html' }}
    );
  }
}

// Background Sync for failed requests
self.addEventListener('sync', (event) => {
  console.log('🔄 Background sync triggered:', event.tag);
  
  if (event.tag === 'background-job-sync') {
    event.waitUntil(syncFailedJobs());
  } else if (event.tag === 'background-message-sync') {
    event.waitUntil(syncFailedMessages());
  }
});

// Sync failed job submissions
async function syncFailedJobs() {
  try {
    const failedJobs = await getFailedJobs();
    
    for (const job of failedJobs) {
      try {
        const response = await fetch('/api/jobs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(job.data)
        });
        
        if (response.ok) {
          await removeFailedJob(job.id);
          console.log('✅ Synced failed job:', job.id);
        }
      } catch (error) {
        console.log('❌ Failed to sync job:', job.id, error);
      }
    }
  } catch (error) {
    console.log('❌ Background sync error:', error);
  }
}

// Sync failed messages
async function syncFailedMessages() {
  // Implementation for syncing failed messages
  console.log('🔄 Syncing failed messages...');
}

// Push notification handler
self.addEventListener('push', (event) => {
  console.log('🔔 Push notification received');
  
  let notificationData = {
    title: 'FixMate-SA',
    body: 'You have a new notification',
    icon: '/fixmate-logo.jpg',
    badge: '/fixmate-logo.jpg',
    tag: 'fixmate-notification',
    requireInteraction: false,
    actions: []
  };
  
  if (event.data) {
    try {
      const data = event.data.json();
      notificationData = {
        ...notificationData,
        ...data,
        actions: [
          {
            action: 'view',
            title: 'View',
            icon: '/fixmate-logo.jpg'
          },
          {
            action: 'dismiss',
            title: 'Dismiss'
          }
        ]
      };
    } catch (error) {
      console.log('❌ Error parsing push data:', error);
    }
  }
  
  event.waitUntil(
    self.registration.showNotification(notificationData.title, notificationData)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('🔔 Notification clicked:', event.action);
  
  event.notification.close();
  
  if (event.action === 'view') {
    // Open the app or specific page
    event.waitUntil(
      self.clients.openWindow(event.notification.data?.url || '/')
    );
  } else if (event.action === 'dismiss') {
    // Just close the notification
    return;
  } else {
    // Default click action
    event.waitUntil(
      self.clients.openWindow('/')
    );
  }
});

// Helper functions for IndexedDB operations
async function getFailedJobs() {
  // Implementation for retrieving failed jobs from IndexedDB
  return [];
}

async function removeFailedJob(jobId) {
  // Implementation for removing synced job from IndexedDB
  console.log('Removing synced job:', jobId);
}

// Periodic background sync
self.addEventListener('periodicsync', (event) => {
  if (event.tag === 'content-sync') {
    event.waitUntil(syncContent());
  }
});

async function syncContent() {
  console.log('📱 Periodic sync: Updating app content...');
  // Sync critical app data in the background
}