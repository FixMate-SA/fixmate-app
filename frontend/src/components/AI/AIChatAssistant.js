import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import api from '../../services/api';

const AIChatAssistant = ({ isOpen, onClose }) => {
  const { user } = useAuth();
  const { language, translations } = useLanguage();
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);

  // Start conversation
  const startConversation = async () => {
    try {
      const response = await api.post('/ai-chat/start', {
        language: language || 'english',
        user_type: user?.role || 'client'
      });

      if (response.data.success) {
        setSessionId(response.data.session_id);
        setMessages([
          {
            type: 'assistant',
            content: response.data.welcome_message || 'Hello! How can I help you today?',
            timestamp: new Date()
          }
        ]);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to start conversation');
    }
  };

  // Send message
  const sendMessage = async (messageText) => {
    if (!sessionId || !messageText.trim()) return;

    const userMessage = {
      type: 'user',
      content: messageText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsTyping(true);

    try {
      const response = await api.post(`/ai-chat/${sessionId}/message`, {
        message: messageText,
        language: language || 'english'
      });

      if (response.data.success) {
        const assistantMessage = {
          type: 'assistant',
          content: response.data.response,
          timestamp: new Date(),
          intent: response.data.intent,
          confidence: response.data.confidence
        };

        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (err) {
      const errorMessage = {
        type: 'assistant',
        content: translations.chat_error || 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  // End conversation
  const endConversation = async (rating = null) => {
    if (!sessionId) return;

    try {
      await api.post(`/ai-chat/${sessionId}/end`, {
        satisfaction_rating: rating,
        resolution_status: 'completed'
      });
      
      setSessionId(null);
      setMessages([]);
      if (onClose) onClose();
    } catch (err) {
      console.error('Failed to end conversation:', err);
      // Still close the chat even if ending fails
      if (onClose) onClose();
    }
  };

  // Handle submit
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(currentMessage);
  };

  // Quick response buttons
  const quickResponses = [
    { text: translations.need_help || 'I need help', message: 'I need help with something' },
    { text: translations.job_question || 'About jobs', message: 'I have a question about jobs' },
    { text: translations.payment_question || 'About payments', message: 'I have a question about payments' },
    { text: translations.technical_issue || 'Technical issue', message: 'I\'m having a technical issue' }
  ];

  useEffect(() => {
    if (isOpen && !sessionId) {
      startConversation();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className={`bg-white rounded-lg shadow-xl border transition-all duration-300 ${
        isMinimized ? 'w-80 h-14' : 'w-80 h-96'
      }`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-blue-600 text-white rounded-t-lg">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-400 rounded-full mr-2 animate-pulse"></div>
            <h3 className="font-semibold">
              {translations.ai_assistant || 'AI Assistant'}
            </h3>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="text-white hover:bg-blue-700 p-1 rounded"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} 
                      d={isMinimized ? "M5 15l7-7 7 7" : "M19 9l-7 7-7-7"} />
              </svg>
            </button>
            <button
              onClick={() => endConversation()}
              className="text-white hover:bg-blue-700 p-1 rounded"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages */}
            <div className="flex-1 p-4 h-64 overflow-y-auto">
              {error && (
                <div className="mb-3 p-2 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
                  {error}
                </div>
              )}

              <div className="space-y-3">
                {messages.map((message, index) => (
                  <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs lg:max-w-md px-3 py-2 rounded-lg text-sm ${
                      message.type === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : message.isError 
                          ? 'bg-red-100 text-red-800'
                          : 'bg-gray-100 text-gray-800'
                    }`}>
                      <div>{message.content}</div>
                      {message.intent && message.confidence && (
                        <div className="text-xs opacity-75 mt-1">
                          Intent: {message.intent} ({Math.round(message.confidence * 100)}%)
                        </div>
                      )}
                      <div className="text-xs opacity-75 mt-1">
                        {message.timestamp.toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 px-3 py-2 rounded-lg">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Quick Responses */}
              {messages.length === 1 && (
                <div className="mt-4">
                  <div className="text-xs text-gray-500 mb-2">
                    {translations.quick_responses || 'Quick responses:'}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {quickResponses.map((response, index) => (
                      <button
                        key={index}
                        onClick={() => sendMessage(response.message)}
                        className="text-xs px-2 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
                      >
                        {response.text}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="border-t p-3">
              <form onSubmit={handleSubmit} className="flex space-x-2">
                <input
                  type="text"
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  placeholder={translations.type_message || 'Type your message...'}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  disabled={!sessionId || isTyping}
                />
                <button
                  type="submit"
                  disabled={!sessionId || !currentMessage.trim() || isTyping}
                  className="bg-blue-600 text-white px-3 py-2 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </form>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

// Chat Button Component
export const AIChatButton = ({ onClick }) => {
  const { translations } = useLanguage();
  
  return (
    <button
      onClick={onClick}
      className="fixed bottom-4 right-4 bg-blue-600 text-white p-4 rounded-full shadow-lg hover:bg-blue-700 transition-all duration-300 z-40 group"
    >
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
      <div className="absolute bottom-full right-0 mb-2 px-2 py-1 bg-gray-800 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
        {translations.ai_assistant || 'AI Assistant'}
      </div>
    </button>
  );
};

export default AIChatAssistant;