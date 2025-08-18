import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import apiService from '../../services/api';

const PushNotificationManager = () => {
  const [isSupported, setIsSupported] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [permission, setPermission] = useState('default');
  const [loading, setLoading] = useState(false);
  const [subscription, setSubscription] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    checkPushSupport();
    checkExistingSubscription();
    
    // Listen for messages from service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', handleServiceWorkerMessage);
    }

    return () => {
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.removeEventListener('message', handleServiceWorkerMessage);
      }
    };
  }, []);

  const handleServiceWorkerMessage = (event) => {
    if (event.data.type === 'NOTIFICATION_CLICK') {
      console.log('📱 Handling notification click navigation:', event.data.url);
      // Navigate to the URL if needed
      if (event.data.url && window.location.pathname !== event.data.url) {
        window.location.href = event.data.url;
      }
    }
  };

  const checkPushSupport = () => {
    const supported = 'serviceWorker' in navigator && 
                     'PushManager' in window && 
                     'Notification' in window;
    setIsSupported(supported);
    
    if (supported) {
      setPermission(Notification.permission);
    }
    
    console.log('🔔 Push notification support:', supported);
  };

  const checkExistingSubscription = async () => {
    if (!('serviceWorker' in navigator)) return;

    try {
      const registration = await navigator.serviceWorker.ready;
      const existingSubscription = await registration.pushManager.getSubscription();
      
      if (existingSubscription) {
        setSubscription(existingSubscription);
        setIsSubscribed(true);
        console.log('✅ Existing push subscription found');
      } else {
        console.log('ℹ️ No existing push subscription');
      }
    } catch (error) {
      console.error('❌ Error checking subscription:', error);
    }
  };

  const requestNotificationPermission = async () => {
    if (!isSupported) return false;

    try {
      const permission = await Notification.requestPermission();
      setPermission(permission);
      
      if (permission === 'granted') {
        console.log('✅ Notification permission granted');
        return true;
      } else {
        console.log('❌ Notification permission denied');
        return false;
      }
    } catch (error) {
      console.error('❌ Error requesting permission:', error);
      return false;
    }
  };

  const subscribeToPush = async () => {
    if (!isSupported || permission !== 'granted') {
      const permissionGranted = await requestNotificationPermission();
      if (!permissionGranted) return;
    }

    setLoading(true);

    try {
      const registration = await navigator.serviceWorker.ready;
      
      // VAPID public key - In production, this should come from your backend
      const vapidPublicKey = 'BEl62iUYgUivxIkv69yViEuiBIa40HI80NMtRGe6rLZRgSdrNjqDQKcnASV33EXe8aD9p7BuYa3v4kHgm-9PjLc';
      
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(vapidPublicKey)
      });

      setSubscription(subscription);
      setIsSubscribed(true);

      // Send subscription to backend
      await sendSubscriptionToServer(subscription);
      
      console.log('✅ Push subscription successful');
      
      // Show test notification
      showTestNotification();
      
    } catch (error) {
      console.error('❌ Push subscription failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const unsubscribeFromPush = async () => {
    if (!subscription) return;

    setLoading(true);

    try {
      await subscription.unsubscribe();
      
      // Remove subscription from backend
      await removeSubscriptionFromServer(subscription);
      
      setSubscription(null);
      setIsSubscribed(false);
      
      console.log('✅ Push unsubscription successful');
    } catch (error) {
      console.error('❌ Push unsubscription failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const sendSubscriptionToServer = async (subscription) => {
    try {
      const response = await fetch('/api/push/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          subscription: subscription.toJSON(),
          userId: user?.id,
          userRole: user?.role
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save subscription to server');
      }

      console.log('✅ Subscription saved to server');
    } catch (error) {
      console.error('❌ Error saving subscription:', error);
    }
  };

  const removeSubscriptionFromServer = async (subscription) => {
    try {
      const response = await fetch('/api/push/unsubscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          subscription: subscription.toJSON(),
          userId: user?.id
        })
      });

      if (!response.ok) {
        throw new Error('Failed to remove subscription from server');
      }

      console.log('✅ Subscription removed from server');
    } catch (error) {
      console.error('❌ Error removing subscription:', error);
    }
  };

  const showTestNotification = () => {
    if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
      navigator.serviceWorker.controller.postMessage({
        type: 'SHOW_TEST_NOTIFICATION',
        data: {
          title: '🎉 FixMate-SA Notifications Active!',
          body: 'You will now receive notifications for job updates, messages, and more.',
          url: '/dashboard'
        }
      });
    }
  };

  const sendTestNotification = async () => {
    if (!isSubscribed) return;

    try {
      const response = await fetch('/api/push/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          userId: user?.id,
          type: 'test',
          title: '🧪 Test Notification',
          message: 'This is a test notification from FixMate-SA!'
        })
      });

      if (response.ok) {
        console.log('✅ Test notification sent');
      }
    } catch (error) {
      console.error('❌ Error sending test notification:', error);
    }
  };

  // Helper function to convert VAPID key
  const urlBase64ToUint8Array = (base64String) => {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  };

  if (!isSupported) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <span className="text-yellow-600">⚠️</span>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Push Notifications Not Supported
            </h3>
            <p className="text-sm text-yellow-700 mt-1">
              Your browser doesn't support push notifications. Please use a modern browser like Chrome, Firefox, or Edge.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <span className="mr-2">🔔</span>
            Push Notifications
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Get instant notifications for job updates, messages, and important alerts
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          {isSubscribed ? (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
              <span className="mr-1">✅</span>
              Active
            </span>
          ) : (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
              <span className="mr-1">🔕</span>
              Inactive
            </span>
          )}
        </div>
      </div>

      <div className="space-y-4">
        {permission === 'denied' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center">
              <span className="text-red-600 mr-2">🚫</span>
              <div>
                <p className="text-sm text-red-800 font-medium">Notifications Blocked</p>
                <p className="text-xs text-red-700 mt-1">
                  To enable notifications, click the notification icon in your browser's address bar and allow notifications.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-gray-900">Notification Types:</h4>
            <ul className="text-xs text-gray-600 space-y-1">
              <li className="flex items-center">
                <span className="mr-2">🔧</span>
                Job assignments and updates
              </li>
              <li className="flex items-center">
                <span className="mr-2">💰</span>
                Payment confirmations
              </li>
              <li className="flex items-center">
                <span className="mr-2">💬</span>
                New messages and replies
              </li>
              <li className="flex items-center">
                <span className="mr-2">⭐</span>
                Reviews and ratings
              </li>
            </ul>
          </div>

          <div className="space-y-3">
            {!isSubscribed ? (
              <button
                onClick={subscribeToPush}
                disabled={loading || permission === 'denied'}
                className="w-full bg-orange-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Enabling...
                  </>
                ) : (
                  <>
                    <span className="mr-2">🔔</span>
                    Enable Notifications
                  </>
                )}
              </button>
            ) : (
              <div className="space-y-2">
                <button
                  onClick={sendTestNotification}
                  className="w-full bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-600 flex items-center justify-center"
                >
                  <span className="mr-2">🧪</span>
                  Send Test Notification
                </button>
                
                <button
                  onClick={unsubscribeFromPush}
                  disabled={loading}
                  className="w-full bg-gray-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-600 disabled:opacity-50 flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Disabling...
                    </>
                  ) : (
                    <>
                      <span className="mr-2">🔕</span>
                      Disable Notifications
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        <div className="text-xs text-gray-500 border-t pt-3">
          <p>💡 <strong>Tip:</strong> Notifications work even when the app is closed. You can disable them anytime in your browser settings.</p>
        </div>
      </div>
    </div>
  );
};

export default PushNotificationManager;