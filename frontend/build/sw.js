// FixMate-SA Service Worker - PWA Core Functionality
// Handles offline caching, background sync, and push notifications

const CACHE_NAME = 'fixmate-sa-v1.0.0';
const OFFLINE_URL = '/offline.html';

// Resources to cache immediately
const STATIC_CACHE_URLS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/fixmate-logo.jpg',
  OFFLINE_URL
];

// API endpoints to cache with network-first strategy
const API_CACHE_URLS = [
  '/api/dashboard/',
  '/api/users',
  '/api/fixers',
  '/api/jobs'
];

// Install event - cache static resources
self.addEventListener('install', event => {
  console.log('FixMate-SA Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('FixMate-SA Service Worker: Caching static resources');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .then(() => {
        console.log('FixMate-SA Service Worker: Installation complete');
        return self.skipWaiting();
      })
      .catch(error => {
        console.error('FixMate-SA Service Worker: Installation failed', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('FixMate-SA Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== CACHE_NAME) {
              console.log('FixMate-SA Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('FixMate-SA Service Worker: Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - handle requests with different caching strategies
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle API requests with network-first strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // Handle navigation requests
  if (request.mode === 'navigate') {
    event.respondWith(navigationHandler(request));
    return;
  }

  // Handle static resources with cache-first strategy
  event.respondWith(cacheFirstStrategy(request));
});

// Network-first strategy for API calls
async function networkFirstStrategy(request) {
  try {
    const response = await fetch(request);
    
    // Cache successful API responses
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('FixMate-SA Service Worker: Network failed, trying cache', error);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback for API requests
    return new Response(
      JSON.stringify({ 
        error: 'Network unavailable', 
        message: 'Please check your internet connection',
        offline: true 
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Cache-first strategy for static resources
async function cacheFirstStrategy(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const response = await fetch(request);
    
    // Cache successful responses
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('FixMate-SA Service Worker: Failed to fetch resource', error);
    return new Response('Resource not available offline', { status: 503 });
  }
}

// Navigation handler for page requests
async function navigationHandler(request) {
  try {
    const response = await fetch(request);
    return response;
  } catch (error) {
    console.log('FixMate-SA Service Worker: Navigation failed, serving offline page');
    
    const cache = await caches.open(CACHE_NAME);
    const offlinePage = await cache.match(OFFLINE_URL);
    
    return offlinePage || new Response('Offline - Please check your connection', {
      status: 503,
      headers: { 'Content-Type': 'text/html' }
    });
  }
}

// Background sync for offline actions
self.addEventListener('sync', event => {
  console.log('FixMate-SA Service Worker: Background sync triggered', event.tag);
  
  switch (event.tag) {
    case 'job-create':
      event.waitUntil(syncOfflineJobs());
      break;
    case 'job-update':
      event.waitUntil(syncJobUpdates());
      break;
    case 'location-update':
      event.waitUntil(syncLocationUpdates());
      break;
    default:
      console.log('FixMate-SA Service Worker: Unknown sync tag', event.tag);
  }
});

// Sync offline job creations
async function syncOfflineJobs() {
  try {
    console.log('FixMate-SA Service Worker: Syncing offline jobs...');
    
    // Get offline jobs from IndexedDB (would need to implement)
    const offlineJobs = await getOfflineJobs();
    
    for (const job of offlineJobs) {
      try {
        const response = await fetch('/api/jobs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(job)
        });
        
        if (response.ok) {
          await removeOfflineJob(job.id);
          console.log('FixMate-SA Service Worker: Synced offline job', job.id);
        }
      } catch (error) {
        console.error('FixMate-SA Service Worker: Failed to sync job', job.id, error);
      }
    }
  } catch (error) {
    console.error('FixMate-SA Service Worker: Background sync failed', error);
  }
}

// Sync job updates
async function syncJobUpdates() {
  console.log('FixMate-SA Service Worker: Syncing job updates...');
  // Implementation would sync job status updates
}

// Sync location updates
async function syncLocationUpdates() {
  console.log('FixMate-SA Service Worker: Syncing location updates...');
  // Implementation would sync fixer location updates
}

// Push notification handler
self.addEventListener('push', event => {
  console.log('FixMate-SA Service Worker: Push notification received');
  
  let notificationData = {
    title: 'FixMate-SA',
    body: 'You have a new notification',
    icon: '/fixmate-logo.jpg',
    badge: '/fixmate-logo.jpg',
    tag: 'fixmate-notification'
  };
  
  if (event.data) {
    try {
      notificationData = { ...notificationData, ...event.data.json() };
    } catch (error) {
      console.error('FixMate-SA Service Worker: Failed to parse push data', error);
    }
  }
  
  const options = {
    body: notificationData.body,
    icon: notificationData.icon,
    badge: notificationData.badge,
    tag: notificationData.tag,
    data: notificationData.data,
    actions: notificationData.actions || [
      { action: 'view', title: 'View' },
      { action: 'dismiss', title: 'Dismiss' }
    ],
    requireInteraction: notificationData.requireInteraction || false,
    silent: notificationData.silent || false
  };
  
  event.waitUntil(
    self.registration.showNotification(notificationData.title, options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', event => {
  console.log('FixMate-SA Service Worker: Notification clicked', event);
  
  event.notification.close();
  
  const action = event.action;
  const notificationData = event.notification.data;
  
  switch (action) {
    case 'view':
      event.waitUntil(handleNotificationView(notificationData));
      break;
    case 'dismiss':
      // Just close the notification
      break;
    default:
      // Default click action
      event.waitUntil(handleNotificationView(notificationData));
  }
});

// Handle notification view action
async function handleNotificationView(data) {
  try {
    const windowClients = await self.clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    });
    
    // Check if app is already open
    for (const client of windowClients) {
      if (client.url.includes(self.location.origin)) {
        // Focus existing window and navigate
        await client.focus();
        if (data && data.url) {
          client.navigate(data.url);
        }
        return;
      }
    }
    
    // Open new window
    const url = data && data.url ? data.url : '/';
    await self.clients.openWindow(url);
  } catch (error) {
    console.error('FixMate-SA Service Worker: Failed to handle notification click', error);
  }
}

// Placeholder functions for IndexedDB operations
async function getOfflineJobs() {
  // Would integrate with IndexedDB to get offline jobs
  return [];
}

async function removeOfflineJob(jobId) {
  // Would remove job from IndexedDB after successful sync
  console.log('Removing offline job:', jobId);
}

// Message handler for communication with main thread
self.addEventListener('message', event => {
  console.log('FixMate-SA Service Worker: Message received', event.data);
  
  const { type, payload } = event.data;
  
  switch (type) {
    case 'SKIP_WAITING':
      self.skipWaiting();
      break;
    case 'CACHE_JOB':
      cacheJobData(payload);
      break;
    case 'GET_CACHE_STATUS':
      getCacheStatus().then(status => {
        event.ports[0].postMessage(status);
      });
      break;
    default:
      console.log('FixMate-SA Service Worker: Unknown message type', type);
  }
});

// Cache job data for offline access
async function cacheJobData(jobData) {
  try {
    const cache = await caches.open(CACHE_NAME);
    const response = new Response(JSON.stringify(jobData));
    await cache.put(`/api/jobs/${jobData.id}`, response);
    console.log('FixMate-SA Service Worker: Cached job data', jobData.id);
  } catch (error) {
    console.error('FixMate-SA Service Worker: Failed to cache job data', error);
  }
}

// Get cache status
async function getCacheStatus() {
  try {
    const cache = await caches.open(CACHE_NAME);
    const keys = await cache.keys();
    
    return {
      cacheSize: keys.length,
      lastUpdated: new Date().toISOString(),
      version: CACHE_NAME
    };
  } catch (error) {
    console.error('FixMate-SA Service Worker: Failed to get cache status', error);
    return { error: error.message };
  }
}

console.log('FixMate-SA Service Worker: Loaded and ready!');