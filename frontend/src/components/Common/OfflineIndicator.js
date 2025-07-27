import React, { useState, useEffect } from 'react';
import offlineService from '../../services/offline_service';

const OfflineIndicator = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [queueLength, setQueueLength] = useState(0);

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      updateQueueLength();
    };

    const handleOffline = () => {
      setIsOnline(false);
      updateQueueLength();
    };

    const updateQueueLength = () => {
      const status = offlineService.getConnectionStatus();
      setQueueLength(status.queueLength);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Update queue length periodically
    const interval = setInterval(updateQueueLength, 5000);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(interval);
    };
  }, []);

  if (isOnline && queueLength === 0) {
    return null; // Don't show anything when online and no queue
  }

  return (
    <div className={`fixed top-20 right-4 z-50 px-4 py-2 rounded-md shadow-lg ${
      isOnline ? 'bg-green-500' : 'bg-yellow-500'
    } text-white`}>
      <div className="flex items-center space-x-2">
        <div className={`w-2 h-2 rounded-full ${
          isOnline ? 'bg-green-200' : 'bg-yellow-200'
        }`}></div>
        <span className="text-sm font-medium">
          {isOnline ? (
            queueLength > 0 ? `Syncing ${queueLength} items...` : 'Back online'
          ) : (
            'Offline mode'
          )}
        </span>
      </div>
      {queueLength > 0 && (
        <div className="mt-1 text-xs opacity-90">
          Changes will sync when connected
        </div>
      )}
    </div>
  );
};

export default OfflineIndicator;