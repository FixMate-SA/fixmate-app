import React, { useState } from 'react';
import { apiService } from '../../services/api';

const SMSInterface = () => {
  const [phoneNumber, setPhoneNumber] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  const handleSendSMS = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await apiService.sendSMS(phoneNumber, message);
      if (response.data.success) {
        setSuccess('SMS sent successfully!');
        setMessage('');
      } else {
        setError('Failed to send SMS. Please try again.');
      }
    } catch (err) {
      setError('Error sending SMS. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  };

  const quickMessages = [
    {
      title: 'Welcome Message',
      content: 'Welcome to FixMate-SA! 🔧 Reply SERVICE to request a service, STATUS to check job status, or HELP for more options.'
    },
    {
      title: 'Service Request',
      content: 'To request a service, reply with: SERVICE [description] [area] [contact]. Example: SERVICE electrical repair Johannesburg 0821234567'
    },
    {
      title: 'Job Status Update',
      content: 'Your FixMate-SA job has been updated. Visit our app at https://fixmate-sa.com to track your job progress.'
    },
    {
      title: 'Fixer Assigned',
      content: 'Great news! A fixer has been assigned to your job. They will contact you shortly to confirm details.'
    }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-blue-600 text-white rounded-lg p-6">
        <h1 className="text-3xl font-bold mb-2">SMS Service Portal</h1>
        <p className="text-green-100">
          Reach users without smartphones through our SMS service. 
          Send updates, notifications, and provide support via text messaging.
        </p>
      </div>

      {/* SMS Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-full">
              <span className="text-2xl">📱</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600">SMS Users</p>
              <p className="text-xl font-semibold">1,234</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-full">
              <span className="text-2xl">📤</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600">Sent Today</p>
              <p className="text-xl font-semibold">87</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-full">
              <span className="text-2xl">📥</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600">Received</p>
              <p className="text-xl font-semibold">156</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-full">
              <span className="text-2xl">🎯</span>
            </div>
            <div className="ml-3">
              <p className="text-sm text-gray-600">Success Rate</p>
              <p className="text-xl font-semibold">98%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Send SMS Form */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Send SMS</h2>
        <form onSubmit={handleSendSMS} className="space-y-4">
          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
              Phone Number
            </label>
            <input
              type="tel"
              id="phone"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              placeholder="e.g., 0821234567 or +27821234567"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
          </div>
          
          <div>
            <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
              Message
            </label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message here..."
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
            <p className="text-sm text-gray-500 mt-1">
              {message.length}/160 characters
            </p>
          </div>
          
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
              {error}
            </div>
          )}
          
          {success && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
              {success}
            </div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Sending...</span>
              </div>
            ) : (
              'Send SMS'
            )}
          </button>
        </form>
      </div>

      {/* Quick Message Templates */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Message Templates</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quickMessages.map((template, index) => (
            <div key={index} className="p-4 bg-gray-50 rounded-lg">
              <h3 className="font-medium text-gray-900 mb-2">{template.title}</h3>
              <p className="text-sm text-gray-600 mb-3">{template.content}</p>
              <button
                onClick={() => setMessage(template.content)}
                className="text-green-600 hover:text-green-700 text-sm font-medium"
              >
                Use Template
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* SMS Commands Help */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">SMS Commands for Users</h2>
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <span className="inline-flex items-center justify-center h-8 w-8 bg-green-100 text-green-600 rounded-full text-sm font-medium">
                📱
              </span>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">HELLO or HI</h3>
              <p className="text-sm text-gray-600">Start a conversation and get the welcome message</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <span className="inline-flex items-center justify-center h-8 w-8 bg-blue-100 text-blue-600 rounded-full text-sm font-medium">
                🔧
              </span>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">SERVICE</h3>
              <p className="text-sm text-gray-600">Request a service - get instructions on how to submit a request</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <span className="inline-flex items-center justify-center h-8 w-8 bg-yellow-100 text-yellow-600 rounded-full text-sm font-medium">
                📊
              </span>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">STATUS</h3>
              <p className="text-sm text-gray-600">Check the status of current jobs</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <span className="inline-flex items-center justify-center h-8 w-8 bg-purple-100 text-purple-600 rounded-full text-sm font-medium">
                ❓
              </span>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">HELP</h3>
              <p className="text-sm text-gray-600">Get help and see available commands</p>
            </div>
          </div>
          
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <span className="inline-flex items-center justify-center h-8 w-8 bg-red-100 text-red-600 rounded-full text-sm font-medium">
                🛑
              </span>
            </div>
            <div>
              <h3 className="font-medium text-gray-900">STOP</h3>
              <p className="text-sm text-gray-600">Unsubscribe from SMS notifications</p>
            </div>
          </div>
        </div>
      </div>

      {/* SMS vs App Comparison */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">SMS vs App Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            <h3 className="font-medium text-green-600">✅ Available via SMS</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Request basic services</li>
              <li>• Check job status</li>
              <li>• Receive notifications</li>
              <li>• Get help and support</li>
              <li>• Emergency contact</li>
            </ul>
          </div>
          
          <div className="space-y-3">
            <h3 className="font-medium text-blue-600">📱 App-Only Features</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Voice service requests</li>
              <li>• Real-time fixer tracking</li>
              <li>• Photo sharing</li>
              <li>• Detailed job history</li>
              <li>• Learning platform access</li>
              <li>• Advanced filtering</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SMSInterface;