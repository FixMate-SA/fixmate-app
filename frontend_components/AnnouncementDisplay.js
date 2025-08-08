import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { API_BASE_URL } from '../../utils/apiConfig';

const AnnouncementDisplay = () => {
  const { user, token } = useAuth();
  const { t } = useLanguage();
  
  const [announcements, setAnnouncements] = useState([]);
  const [selectedAnnouncement, setSelectedAnnouncement] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [chatLoading, setChatLoading] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);

  useEffect(() => {
    fetchAnnouncements();
  }, []);

  const fetchAnnouncements = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/announcements`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setAnnouncements(data.announcements || []);
      } else {
        console.error('Failed to fetch announcements');
      }
    } catch (error) {
      console.error('Error fetching announcements:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchChatMessages = async (announcementId) => {
    try {
      setChatLoading(true);
      const response = await fetch(`${API_BASE_URL}/announcements/${announcementId}/chat`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setChatMessages(data.messages || []);
      } else {
        console.error('Failed to fetch chat messages');
      }
    } catch (error) {
      console.error('Error fetching chat messages:', error);
    } finally {
      setChatLoading(false);
    }
  };

  const sendChatMessage = async (e) => {
    e.preventDefault();
    
    if (!newMessage.trim()) return;

    try {
      setSendingMessage(true);
      const response = await fetch(`${API_BASE_URL}/announcements/${selectedAnnouncement.id}/chat`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: newMessage.trim() })
      });

      if (response.ok) {
        setNewMessage('');
        await fetchChatMessages(selectedAnnouncement.id);
        // Scroll to bottom of messages
        setTimeout(() => {
          const messagesContainer = document.getElementById('messages-container');
          if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
          }
        }, 100);
      } else {
        const errorData = await response.json();
        alert(`Failed to send message: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Error sending message');
    } finally {
      setSendingMessage(false);
    }
  };

  const openChat = (announcement) => {
    setSelectedAnnouncement(announcement);
    fetchChatMessages(announcement.id);
  };

  const closeChat = () => {
    setSelectedAnnouncement(null);
    setChatMessages([]);
    setNewMessage('');
  };

  const getTargetAudienceIcon = (audience) => {
    switch (audience) {
      case 'clients': return '👥';
      case 'fixers': return '🔧';
      case 'all': return '🌐';
      default: return '📢';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'border-l-red-500 bg-red-50';
      case 'normal': return 'border-l-blue-500 bg-blue-50';
      case 'low': return 'border-l-gray-500 bg-gray-50';
      default: return 'border-l-blue-500 bg-blue-50';
    }
  };

  const formatMessageTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffHours = (now - date) / (1000 * 60 * 60);
    
    if (diffHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading announcements...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium flex items-center gap-2">
          <span>📢</span>
          {t('announcements', 'Announcements')}
        </h3>
        <div className="text-sm text-gray-600">
          {announcements.length} {t('totalAnnouncements', 'announcements')}
        </div>
      </div>

      {/* Announcements List */}
      {announcements.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm p-8 text-center text-gray-500">
          <span className="text-4xl mb-4 block">📢</span>
          <p className="text-lg font-medium mb-2">{t('noAnnouncements', 'No announcements available')}</p>
          <p className="text-sm">{t('checkBackLater', 'Check back later for updates from the admin.')}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {announcements.map((announcement) => (
            <div
              key={announcement.id}
              className={`bg-white rounded-lg shadow-sm border-l-4 ${getPriorityColor(announcement.priority)} overflow-hidden`}
            >
              <div className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      {announcement.is_pinned && (
                        <span className="text-yellow-500 text-lg">📌</span>
                      )}
                      <h4 className="text-lg font-semibold text-gray-900">
                        {announcement.title}
                      </h4>
                      <span className="flex items-center gap-1 text-sm text-gray-600 bg-white px-2 py-1 rounded-full border">
                        {getTargetAudienceIcon(announcement.target_audience)}
                        <span className="capitalize">{announcement.target_audience}</span>
                      </span>
                      {announcement.priority === 'high' && (
                        <span className="bg-red-100 text-red-700 px-2 py-1 text-xs rounded-full font-medium">
                          {t('highPriority', 'High Priority')}
                        </span>
                      )}
                    </div>
                    
                    <div className="text-gray-700 mb-4 whitespace-pre-wrap">
                      {announcement.content}
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-gray-500">
                      <div className="flex items-center gap-4">
                        <span>
                          {new Date(announcement.created_at).toLocaleDateString()}
                        </span>
                        {announcement.expires_at && (
                          <>
                            <span>•</span>
                            <span className="text-orange-600">
                              {t('expires', 'Expires')} {new Date(announcement.expires_at).toLocaleDateString()}
                            </span>
                          </>
                        )}
                        {announcement.chat_message_count > 0 && (
                          <>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              💬 {announcement.chat_message_count} {t('messages', 'messages')}
                            </span>
                          </>
                        )}
                      </div>
                      
                      {announcement.chat_enabled && (
                        <button
                          onClick={() => openChat(announcement)}
                          className="bg-blue-600 text-white px-3 py-1 rounded-full hover:bg-blue-700 transition flex items-center gap-1"
                        >
                          💬 {t('viewChat', 'View Chat')}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Recent Messages Preview */}
                {announcement.recent_chats && announcement.recent_chats.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-100">
                    <div className="text-sm text-gray-600 mb-2">
                      {t('recentMessages', 'Recent messages')}:
                    </div>
                    <div className="space-y-2">
                      {announcement.recent_chats.slice(-2).map((chat, index) => (
                        <div key={index} className="flex items-start gap-2 text-sm">
                          <span className="font-medium text-gray-700 flex-shrink-0">
                            {chat.is_admin ? '🛠️' : '👤'} {chat.user_name}:
                          </span>
                          <span className="text-gray-600 truncate">
                            {chat.message}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Chat Modal */}
      {selectedAnnouncement && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg w-full max-w-2xl h-[600px] flex flex-col">
            {/* Chat Header */}
            <div className="p-4 border-b border-gray-200 flex items-center justify-between bg-gray-50">
              <div className="flex items-center gap-2">
                <h3 className="font-medium text-gray-900">💬 {selectedAnnouncement.title}</h3>
                {selectedAnnouncement.admin_only_chat && (
                  <span className="bg-orange-100 text-orange-700 px-2 py-1 text-xs rounded-full">
                    {t('adminOnly', 'Admin Only')}
                  </span>
                )}
              </div>
              <button
                onClick={closeChat}
                className="text-gray-500 hover:text-gray-700 text-xl p-1"
              >
                ✕
              </button>
            </div>

            {/* Chat Messages */}
            <div 
              id="messages-container"
              className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50"
            >
              {chatLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  <span className="ml-2 text-gray-600">Loading messages...</span>
                </div>
              ) : chatMessages.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <span className="text-3xl mb-2 block">💭</span>
                  <p>{t('noMessages', 'No messages yet')}</p>
                  <p className="text-sm">{t('startConversation', 'Be the first to start the conversation!')}</p>
                </div>
              ) : (
                chatMessages.map((message) => (
                  <div 
                    key={message.id}
                    className={`flex ${message.user_id === user?.id ? 'justify-end' : 'justify-start'}`}
                  >
                    <div 
                      className={`max-w-[70%] rounded-lg px-4 py-2 ${
                        message.user_id === user?.id
                          ? 'bg-blue-600 text-white'
                          : message.is_admin_message
                          ? 'bg-red-100 text-red-900 border border-red-200'
                          : 'bg-white text-gray-900 border border-gray-200'
                      }`}
                    >
                      <div className="flex items-center gap-2 text-xs opacity-75 mb-1">
                        <span>
                          {message.is_admin_message ? '🛠️' : '👤'} {message.user_name}
                        </span>
                        <span>•</span>
                        <span>{formatMessageTime(message.created_at)}</span>
                      </div>
                      <div className="whitespace-pre-wrap">
                        {message.message}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Chat Input */}
            {selectedAnnouncement.chat_enabled && (
              <div className="p-4 border-t border-gray-200 bg-white">
                {selectedAnnouncement.admin_only_chat && user?.role !== 'admin' ? (
                  <div className="text-center text-gray-500 py-2">
                    🔒 {t('adminOnlyChat', 'Only admin can respond in this chat')}
                  </div>
                ) : (
                  <form onSubmit={sendChatMessage} className="flex gap-3">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder={t('typeMessage', 'Type your message...')}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                      disabled={sendingMessage}
                    />
                    <button
                      type="submit"
                      disabled={!newMessage.trim() || sendingMessage}
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition flex items-center gap-1"
                    >
                      {sendingMessage ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        </>
                      ) : (
                        <>
                          📤 {t('send', 'Send')}
                        </>
                      )}
                    </button>
                  </form>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnnouncementDisplay;