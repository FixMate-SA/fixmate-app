import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { API_BASE_URL } from '../../utils/apiConfig';

const AnnouncementManagement = () => {
  const { user, token } = useAuth();
  const { t } = useLanguage();
  
  const [announcements, setAnnouncements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    target_audience: 'all',
    priority: 'normal',
    is_pinned: false,
    chat_enabled: true,
    admin_only_chat: false,
    expires_at: ''
  });

  useEffect(() => {
    fetchAnnouncements();
  }, []);

  const fetchAnnouncements = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/admin/announcements`, {
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

  const handleCreateAnnouncement = async (e) => {
    e.preventDefault();
    
    try {
      const payload = {
        ...formData,
        expires_at: formData.expires_at ? new Date(formData.expires_at).toISOString() : null
      };

      const response = await fetch(`${API_BASE_URL}/admin/announcements`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const data = await response.json();
        await fetchAnnouncements();
        setShowCreateForm(false);
        resetForm();
        alert('Announcement created successfully!');
      } else {
        const errorData = await response.json();
        alert(`Failed to create announcement: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error creating announcement:', error);
      alert('Error creating announcement');
    }
  };

  const handleDeleteAnnouncement = async (announcementId, title) => {
    if (!confirm(`Are you sure you want to delete "${title}"?`)) {
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/admin/announcements/${announcementId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        await fetchAnnouncements();
        alert('Announcement deleted successfully!');
      } else {
        const errorData = await response.json();
        alert(`Failed to delete announcement: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error deleting announcement:', error);
      alert('Error deleting announcement');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      target_audience: 'all',
      priority: 'normal',
      is_pinned: false,
      chat_enabled: true,
      admin_only_chat: false,
      expires_at: ''
    });
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
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
      case 'high': return 'text-red-600 bg-red-100';
      case 'normal': return 'text-blue-600 bg-blue-100';
      case 'low': return 'text-gray-600 bg-gray-100';
      default: return 'text-blue-600 bg-blue-100';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-600"></div>
        <span className="ml-2 text-gray-600">Loading announcements...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium flex items-center gap-2">
          <span>📢</span>
          {t('announcementManagement', 'Announcement Management')}
        </h3>
        <button
          onClick={() => {
            resetForm();
            setShowCreateForm(true);
          }}
          className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition flex items-center gap-2"
        >
          <span>➕</span>
          {t('createAnnouncement', 'Create Announcement')}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <div className="text-2xl font-bold text-blue-700">{announcements.length}</div>
          <div className="text-blue-600 text-sm">Total Announcements</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <div className="text-2xl font-bold text-green-700">
            {announcements.filter(a => a.is_active).length}
          </div>
          <div className="text-green-600 text-sm">Active</div>
        </div>
        <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
          <div className="text-2xl font-bold text-yellow-700">
            {announcements.filter(a => a.is_pinned).length}
          </div>
          <div className="text-yellow-600 text-sm">Pinned</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
          <div className="text-2xl font-bold text-purple-700">
            {announcements.reduce((total, a) => total + (a.chat_message_count || 0), 0)}
          </div>
          <div className="text-purple-600 text-sm">Total Messages</div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
          <h4 className="font-medium text-gray-900">All Announcements</h4>
        </div>
        
        {announcements.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            <span className="text-4xl mb-4 block">📢</span>
            <p className="text-lg font-medium mb-2">No announcements yet</p>
            <p className="text-sm">Create your first announcement to communicate with users.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {announcements.map((announcement) => (
              <div key={announcement.id} className="p-6 hover:bg-gray-50 transition">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h5 className="font-medium text-gray-900 flex items-center gap-2">
                        {announcement.is_pinned && <span className="text-yellow-500">📌</span>}
                        {announcement.title}
                      </h5>
                      <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(announcement.priority)}`}>
                        {announcement.priority}
                      </span>
                      <span className="flex items-center gap-1 text-sm text-gray-600">
                        {getTargetAudienceIcon(announcement.target_audience)}
                        {announcement.target_audience}
                      </span>
                    </div>
                    
                    <p className="text-gray-700 mb-3">
                      {announcement.content}
                    </p>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>By {announcement.created_by_name || 'Admin'}</span>
                      <span>•</span>
                      <span>{new Date(announcement.created_at).toLocaleDateString()}</span>
                      <span>•</span>
                      <span className="flex items-center gap-1">
                        💬 {announcement.chat_message_count || 0} messages
                      </span>
                    </div>
                    
                    <div className="flex items-center gap-3 mt-3">
                      <div className="flex items-center gap-2 text-xs">
                        <span className={`h-2 w-2 rounded-full ${announcement.is_active ? 'bg-green-500' : 'bg-red-500'}`}></span>
                        {announcement.is_active ? 'Active' : 'Inactive'}
                      </div>
                      <div className="flex items-center gap-2 text-xs">
                        <span className={`h-2 w-2 rounded-full ${announcement.chat_enabled ? 'bg-green-500' : 'bg-gray-400'}`}></span>
                        Chat {announcement.chat_enabled ? 'Enabled' : 'Disabled'}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => handleDeleteAnnouncement(announcement.id, announcement.title)}
                      className="text-red-600 hover:text-red-800 p-2 hover:bg-red-50 rounded"
                      title="Delete announcement"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h3 className="text-lg font-medium">
                {t('createAnnouncement', 'Create Announcement')}
              </h3>
            </div>
            
            <form onSubmit={handleCreateAnnouncement} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Title *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500"
                  placeholder="Enter announcement title..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Content *
                </label>
                <textarea
                  name="content"
                  value={formData.content}
                  onChange={handleInputChange}
                  required
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500"
                  placeholder="Enter announcement content..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Audience *
                  </label>
                  <select
                    name="target_audience"
                    value={formData.target_audience}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500"
                  >
                    <option value="all">🌐 All Users</option>
                    <option value="clients">👥 Clients Only</option>
                    <option value="fixers">🔧 Fixers Only</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Priority
                  </label>
                  <select
                    name="priority"
                    value={formData.priority}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500"
                  >
                    <option value="normal">Normal</option>
                    <option value="high">High Priority</option>
                    <option value="low">Low Priority</option>
                  </select>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    id="is_pinned"
                    name="is_pinned"
                    checked={formData.is_pinned}
                    onChange={handleInputChange}
                    className="rounded border-gray-300 text-red-600 focus:ring-red-500"
                  />
                  <label htmlFor="is_pinned" className="text-sm font-medium text-gray-700">
                    📌 Pin this announcement at the top
                  </label>
                </div>

                <div className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    id="chat_enabled"
                    name="chat_enabled"
                    checked={formData.chat_enabled}
                    onChange={handleInputChange}
                    className="rounded border-gray-300 text-red-600 focus:ring-red-500"
                  />
                  <label htmlFor="chat_enabled" className="text-sm font-medium text-gray-700">
                    💬 Enable chat responses
                  </label>
                </div>

                {formData.chat_enabled && (
                  <div className="flex items-center gap-3 ml-6">
                    <input
                      type="checkbox"
                      id="admin_only_chat"
                      name="admin_only_chat"
                      checked={formData.admin_only_chat}
                      onChange={handleInputChange}
                      className="rounded border-gray-300 text-red-600 focus:ring-red-500"
                    />
                    <label htmlFor="admin_only_chat" className="text-sm font-medium text-gray-700">
                      🔒 Only admin can respond in chat
                    </label>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowCreateForm(false);
                    resetForm();
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
                >
                  Create Announcement
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnnouncementManagement;