import React from 'react';

// Simple test component to verify component rendering
const PushNotificationTest = () => {
  return (
    <div className="bg-green-100 border border-green-400 rounded-lg p-4 m-4">
      <h3 className="text-green-800 font-bold">🧪 TEST COMPONENT RENDERED</h3>
      <p className="text-green-700">
        If you can see this, React component rendering is working correctly.
      </p>
      <div className="mt-4">
        <button className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
          Test Button
        </button>
      </div>
    </div>
  );
};

export default PushNotificationTest;