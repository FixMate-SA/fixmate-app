import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const ProfileDebug = () => {
  const { user, getUserRole } = useAuth();
  const [debugInfo, setDebugInfo] = useState({});

  useEffect(() => {
    setDebugInfo({
      user: user,
      userRole: getUserRole(),
      location: window.location.href,
      timestamp: new Date().toISOString()
    });
  }, [user]);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-bold text-red-800 mb-4">🐛 Profile Debug Information</h2>
        <pre className="text-sm text-red-700 bg-red-100 p-4 rounded overflow-auto">
          {JSON.stringify(debugInfo, null, 2)}
        </pre>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-bold text-blue-800 mb-4">📱 Push Notification Debug</h2>
        <div className="space-y-2 text-sm text-blue-700">
          <p>ServiceWorker support: {'serviceWorker' in navigator ? '✅' : '❌'}</p>
          <p>PushManager support: {'PushManager' in window ? '✅' : '❌'}</p>
          <p>Notification support: {'Notification' in window ? '✅' : '❌'}</p>
          <p>Secure Context: {window.isSecureContext ? '✅' : '❌'}</p>
          <p>Current URL: {window.location.href}</p>
          <p>User Agent: {navigator.userAgent}</p>
        </div>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
        <h2 className="text-xl font-bold text-green-800 mb-4">🔔 Test Notification Section</h2>
        <p className="text-green-700 mb-4">This section tests if components can render in the profile page location.</p>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <span className="mr-2">🔔</span>
                Debug Push Notifications Component
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                This is a test component to verify rendering works in this location
              </p>
            </div>
          </div>
          
          <div className="space-y-4">
            <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
              Test Enable Notifications
            </button>
            
            <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 ml-2">
              Test Send Notification
            </button>
            
            <div className="mt-4 p-4 bg-gray-50 rounded">
              <h4 className="font-medium text-gray-900 mb-2">Notification Types:</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Job assignments and updates</li>
                <li>• Payment confirmations</li>
                <li>• New messages from fixers</li>
                <li>• System alerts and reminders</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileDebug;