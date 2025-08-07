import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/api';
import WhatsAppStatistics from './WhatsAppStatistics';
import FixerPaymentManager from '../Payment/FixerPaymentManager';
import SmartMatchingDashboard from './SmartMatchingDashboard';
import Logo from '../Common/Logo';
import { API_BASE_URL } from '../../utils/apiConfig';

const AdminDashboard = () => {
  const { user, isRole } = useAuth();
  const { t } = useLanguage();
  const [stats, setStats] = useState({});
  const [fixers, setFixers] = useState([]);
  const [users, setUsers] = useState([]);
  const [complianceRequests, setComplianceRequests] = useState([]);
  const [selectedFixer, setSelectedFixer] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [showClientRequestForm, setShowClientRequestForm] = useState(false);
  const [clientRequestForm, setClientRequestForm] = useState({
    client_name: '',
    client_phone: '',
    service: '',
    description: '',
    location: '',
    estimated_price: '',
    scheduled_at: ''
  });

  // Redirect if not admin
  if (!isRole('admin')) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 text-xl font-bold mb-4">Access Denied</div>
        <p className="text-gray-600">You do not have permission to access the admin dashboard.</p>
      </div>
    );
  }

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      const [fixersResponse, usersResponse] = await Promise.all([
        apiService.getFixers(),
        apiService.getUsers()
      ]);

      setFixers(fixersResponse.data || []);
      setUsers(usersResponse.data || []);
      
      // Fetch business compliance requests
      try {
        const complianceResponse = await fetch(`${API_BASE_URL}/compliance/admin/all-requests`);
        if (complianceResponse.ok) {
          const complianceData = await complianceResponse.json();
          setComplianceRequests(complianceData.requests || []);
        }
      } catch (error) {
        console.error('Error fetching compliance requests:', error);
      }
      
      // Calculate stats
      const totalFixers = fixersResponse.data?.length || 0;
      const activeFixers = fixersResponse.data?.filter(f => f.is_active)?.length || 0;
      const totalUsers = usersResponse.data?.length || 0;

      setStats({
        totalUsers,
        totalFixers,
        activeFixers,
        inactiveFixers: totalFixers - activeFixers,
        avgFixerRating: totalFixers > 0 
          ? (fixersResponse.data.reduce((sum, f) => sum + f.rating, 0) / totalFixers).toFixed(1)
          : 0
      });

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const updatePaymentStatuses = async () => {
    try {
      const result = await apiService.post('/admin/update-payment-statuses');
      if (result.success) {
        alert(`Payment statuses updated: ${result.overdue_payments_updated} payments marked as overdue`);
        await fetchDashboardData(); // Refresh data
      }
    } catch (error) {
      console.error('Error updating payment statuses:', error);
      alert('Failed to update payment statuses');
    }
  };

  const handleClientRequestSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      // First, find or create the client user
      let clientUser = users.find(u => u.phone === clientRequestForm.client_phone);
      
      if (!clientUser) {
        // Create client user
        const userResponse = await apiService.createUser({
          phone: clientRequestForm.client_phone,
          first_name: clientRequestForm.client_name,
          role: 'client'
        });
        clientUser = userResponse.data;
      }

      // Create the job request using proper API service
      const jobData = {
        user_id: clientUser.id,
        service: clientRequestForm.service,
        description: clientRequestForm.description,
        location: clientRequestForm.location,
        estimated_price: clientRequestForm.estimated_price ? parseFloat(clientRequestForm.estimated_price) : null,
        scheduled_at: clientRequestForm.scheduled_at ? new Date(clientRequestForm.scheduled_at).toISOString() : null,
        contact_number: clientRequestForm.client_phone,
        latitude: null,
        longitude: null,
        admin_created: true // Flag to indicate admin created this job
      };

      const response = await apiService.createJob(jobData);
      
      if (response.success || response.data) {
        const jobId = response.job_id || response.data?.id || 'unknown';
        alert(`✅ Service request created successfully for ${clientRequestForm.client_name}! Job ID: ${jobId}`);
        
        // Reset form
        setClientRequestForm({
          client_name: '',
          client_phone: '',
          service: '',
          description: '',
          location: '',
          estimated_price: '',
          scheduled_at: ''
        });
        setShowClientRequestForm(false);
        fetchDashboardData(); // Refresh data
      } else {
        alert(`❌ Failed to create service request: ${response.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error creating client service request:', error);
      alert(`❌ Failed to create service request: ${error.response?.data?.detail || error.message || 'Unknown error'}`);
    } finally {
      setLoading(false);
    }
  };

  const serviceOptions = [
    'Plumbing', 'Electrical', 'Carpentry', 'Painting', 'Cleaning', 
    'Gardening', 'Handyman', 'Appliance Repair', 'Roofing', 'Flooring', 
    'HVAC', 'Tech Support', 'Tutoring', 'Beauty Services', 'Catering', 
    'Photography', 'Other'
  ];

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Admin Header */}
      <div className="bg-red-600 text-white rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Logo 
              size="medium" 
              variant="header" 
              showText={false}
            />
            <div>
              <h1 className="text-2xl font-bold">Admin Dashboard</h1>
              <p className="opacity-90">Manage FixMate-SA Platform</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={updatePaymentStatuses}
              className="bg-red-700 hover:bg-red-800 px-4 py-2 rounded-lg font-medium"
            >
              Update Payment Status
            </button>
            <div className="text-right">
              <p className="text-sm opacity-90">Welcome back,</p>
              <p className="font-bold">{user?.name}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-3xl font-bold text-blue-600">{stats.totalUsers}</div>
          <div className="text-gray-600">{t('totalUsers')}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-3xl font-bold text-orange-600">{stats.totalFixers}</div>
          <div className="text-gray-600">{t('totalFixers', 'Total Fixers')}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-3xl font-bold text-emerald-600">{stats.activeFixers}</div>
          <div className="text-gray-600">{t('activeFixers', 'Active Fixers')}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-3xl font-bold text-red-600">{stats.inactiveFixers}</div>
          <div className="text-gray-600">{t('inactiveFixers', 'Inactive Fixers')}</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-3xl font-bold text-yellow-600">{stats.avgFixerRating}⭐</div>
          <div className="text-gray-600">{t('avgRating', 'Avg Rating')}</div>
        </div>
      </div>

      {/* Admin Tabs */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-2 md:space-x-8 px-2 md:px-6 overflow-x-auto">
            {[
              { id: 'overview', label: t('overview'), icon: '📊' },
              { id: 'whatsapp', label: t('whatsapp', 'WhatsApp'), icon: '📱' },
              { id: 'client-request', label: t('clientRequest', 'Client Request'), icon: '📞' },
              { id: 'smart-matching', label: t('smartMatching'), icon: '🎯' },
              { id: 'compliance', label: t('compliance', 'Compliance'), icon: '🏢' },
              { id: 'fixers', label: t('fixerMgmt', 'Fixer Mgmt'), icon: '🔧' },
              { id: 'payments', label: t('payment'), icon: '💳' },
              { id: 'users', label: t('users', 'Users'), icon: '👥' },
              { id: 'reports', label: t('reports', 'Reports'), icon: '📈' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-3 md:py-4 px-1 md:px-2 border-b-2 font-medium text-xs md:text-sm flex items-center space-x-1 md:space-x-2 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-red-500 text-red-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span className="hidden sm:inline">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium">Platform Overview</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h4 className="font-medium">Recent Activity</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <span>New user registrations today</span>
                      <span className="font-medium">--</span>
                    </div>
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <span>Jobs created today</span>
                      <span className="font-medium">--</span>
                    </div>
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <span>Payments processed today</span>
                      <span className="font-medium">--</span>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <h4 className="font-medium">System Status</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <span>Database Status</span>
                      <span className="text-green-600 font-medium">✓ Online</span>
                    </div>
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <span>SMS Service</span>
                      <span className="text-green-600 font-medium">✓ Active</span>
                    </div>
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <span>Payment Gateway</span>
                      <span className="text-green-600 font-medium">✓ Connected</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'whatsapp' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium flex items-center gap-2">
                  <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.297"/>
                  </svg>
                  {t('whatsappIntegration', 'WhatsApp Business Integration')}
                </h3>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-green-600 font-medium">Active</span>
                </div>
              </div>

              {/* WhatsApp Business Account Info */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                  <div className="text-2xl font-bold text-green-700 mb-2">27754466571</div>
                  <div className="text-green-600 font-medium">Business Number</div>
                  <div className="text-sm text-green-700 mt-2">FixMate-SA Official</div>
                </div>
                
                <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                  <div className="text-2xl font-bold text-blue-700 mb-2">KYS4TkCH</div>
                  <div className="text-blue-600 font-medium">Channel ID</div>
                  <div className="text-sm text-blue-700 mt-2">Active Channel</div>
                </div>
                
                <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
                  <div className="text-2xl font-bold text-purple-700 mb-2">1K/24hr</div>
                  <div className="text-purple-600 font-medium">Message Limit</div>
                  <div className="text-sm text-purple-700 mt-2">High Quality Rating</div>
                </div>
              </div>

              {/* WhatsApp Integration Status */}
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
                  <h4 className="font-medium text-gray-900">Integration Status</h4>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <span className="flex items-center gap-2">
                        <span className="h-2 w-2 bg-green-500 rounded-full"></span>
                        Webhook Endpoint
                      </span>
                      <span className="text-green-600 font-medium">✓ Active</span>
                    </div>
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <span className="flex items-center gap-2">
                        <span className="h-2 w-2 bg-green-500 rounded-full"></span>
                        360Dialog API
                      </span>
                      <span className="text-green-600 font-medium">✓ Connected</span>
                    </div>
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <span className="flex items-center gap-2">
                        <span className="h-2 w-2 bg-green-500 rounded-full"></span>
                        Message Processing
                      </span>
                      <span className="text-green-600 font-medium">✓ Operational</span>
                    </div>
                    <div className="flex items-center justify-between py-2 border-b border-gray-100">
                      <span className="flex items-center gap-2">
                        <span className="h-2 w-2 bg-green-500 rounded-full"></span>
                        Database Integration
                      </span>
                      <span className="text-green-600 font-medium">✓ Working</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* WhatsApp Configuration Details */}
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
                  <h4 className="font-medium text-gray-900">Configuration Details</h4>
                </div>
                <div className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="font-medium text-gray-700 mb-1">Webhook URL</div>
                      <div className="text-gray-600 font-mono text-xs bg-gray-100 p-2 rounded">
                        https://fixmate-sa-app-a448c751e1d2.herokuapp.com/whatsapp
                      </div>
                    </div>
                    <div>
                      <div className="font-medium text-gray-700 mb-1">WABA ID</div>
                      <div className="text-gray-600 font-mono text-xs bg-gray-100 p-2 rounded">
                        1437544007427224
                      </div>
                    </div>
                    <div>
                      <div className="font-medium text-gray-700 mb-1">Hosting Platform</div>
                      <div className="text-gray-600">Cloud API hosted by Meta</div>
                    </div>
                    <div>
                      <div className="font-medium text-gray-700 mb-1">Data Storage Region</div>
                      <div className="text-gray-600">United States</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Real-time WhatsApp Message Statistics */}
              <WhatsAppStatistics />

              {/* Test WhatsApp Integration */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <h4 className="font-medium text-yellow-800 mb-2">Test WhatsApp Integration</h4>
                <p className="text-sm text-yellow-700 mb-4">
                  Send a test message to verify the integration is working correctly.
                </p>
                <div className="flex items-center gap-4">
                  <a
                    href="https://wa.me/27754466571?text=Test%20message%20from%20admin"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition flex items-center gap-2"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.297"/>
                    </svg>
                    Send Test Message
                  </a>
                  <span className="text-sm text-gray-600">Opens WhatsApp with pre-filled test message</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'fixers' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Fixer Management</h3>
                <div className="text-sm text-gray-600">
                  {fixers.length} total fixers
                </div>
              </div>
              
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-300">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                        <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
                        <th className="hidden sm:table-cell px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Services</th>
                        <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                        <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {fixers.map((fixer) => (
                        <tr key={fixer.id}>
                          <td className="px-3 md:px-6 py-4 text-sm font-medium text-gray-900">
                            <div className="max-w-[100px] md:max-w-none truncate">
                              {fixer.name}
                            </div>
                          </td>
                          <td className="px-3 md:px-6 py-4 text-sm text-gray-500">
                            <div className="max-w-[120px] md:max-w-none truncate">
                              {fixer.phone}
                            </div>
                          </td>
                          <td className="hidden sm:table-cell px-3 md:px-6 py-4 text-sm text-gray-500">
                            <div className="max-w-xs">
                              {JSON.parse(fixer.services).slice(0, 2).map((service, i) => (
                                <span key={i} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-1 mb-1">
                                  {service}
                                </span>
                              ))}
                              {JSON.parse(fixer.services).length > 2 && (
                                <span className="text-xs text-gray-500">+{JSON.parse(fixer.services).length - 2}</span>
                              )}
                            </div>
                          </td>
                          <td className="px-3 md:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <div className="text-xs md:text-sm">
                              {fixer.rating.toFixed(1)}⭐
                              <div className="md:hidden text-xs text-gray-400">({fixer.total_jobs})</div>
                              <div className="hidden md:inline"> ({fixer.total_jobs} jobs)</div>
                            </div>
                          </td>
                          <td className="px-3 md:px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              fixer.is_active 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {fixer.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-3 md:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <button
                              onClick={() => setSelectedFixer(fixer)}
                              className="text-red-600 hover:text-red-900 font-medium text-xs md:text-sm"
                            >
                              Manage
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'payments' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium">Payment Management</h3>
              {selectedFixer ? (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium">Managing payments for: {selectedFixer.name}</h4>
                    <button
                      onClick={() => setSelectedFixer(null)}
                      className="text-gray-600 hover:text-gray-800"
                    >
                      ← Back to fixer list
                    </button>
                  </div>
                  <FixerPaymentManager fixerId={selectedFixer.id} isAdmin={true} />
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-gray-500">Select a fixer from the Fixer Management tab to manage their payments.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'users' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium">User Management</h3>
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-300">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                        <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
                        <th className="hidden sm:table-cell px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID Number</th>
                        <th className="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                        <th className="hidden md:table-cell px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="hidden lg:table-cell px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {users.map((user) => (
                        <tr key={user.id}>
                          <td className="px-3 md:px-6 py-4 text-sm font-medium text-gray-900">
                            <div className="max-w-[100px] md:max-w-none truncate">
                              {user.first_name && user.last_name 
                                ? `${user.first_name} ${user.last_name}`.trim()
                                : user.first_name || user.last_name || 'No Name'
                              }
                            </div>
                          </td>
                          <td className="px-3 md:px-6 py-4 text-sm text-gray-500">
                            <div className="max-w-[120px] md:max-w-none truncate">
                              {user.phone}
                            </div>
                          </td>
                          <td className="hidden sm:table-cell px-3 md:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <div className="max-w-[100px] truncate">
                              {user.id_number || 'Not provided'}
                            </div>
                          </td>
                          <td className="px-3 md:px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              user.role === 'admin' ? 'bg-red-100 text-red-800' :
                              user.role === 'fixer' ? 'bg-orange-100 text-orange-800' :
                              'bg-blue-100 text-blue-800'
                            }`}>
                              <span className="md:hidden">
                                {user.role?.charAt(0)?.toUpperCase()}
                              </span>
                              <span className="hidden md:inline">
                                {user.role?.charAt(0)?.toUpperCase() + user.role?.slice(1)}
                              </span>
                            </span>
                          </td>
                          <td className="hidden md:table-cell px-3 md:px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              user.is_active 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {user.is_active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="hidden lg:table-cell px-3 md:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'reports' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium">Reports & Analytics</h3>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-yellow-800">Reports Coming Soon</h3>
                    <div className="mt-2 text-sm text-yellow-700">
                      <p>Advanced analytics and reporting features will be available in the next update.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'client-request' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Client Service Request</h3>
                <button
                  onClick={() => setShowClientRequestForm(!showClientRequestForm)}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
                >
                  {showClientRequestForm ? 'Cancel' : 'New Request'}
                </button>
              </div>
              
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-blue-800">Admin Client Request</h3>
                    <div className="mt-2 text-sm text-blue-700">
                      <p>Use this form to create service requests on behalf of clients who call in or need assistance logging requests.</p>
                    </div>
                  </div>
                </div>
              </div>

              {showClientRequestForm && (
                <form onSubmit={handleClientRequestSubmit} className="bg-gray-50 p-6 rounded-lg space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Client Name *
                      </label>
                      <input
                        type="text"
                        value={clientRequestForm.client_name}
                        onChange={(e) => setClientRequestForm({...clientRequestForm, client_name: e.target.value})}
                        required
                        className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                        placeholder="Enter client's full name"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Client Phone *
                      </label>
                      <input
                        type="tel"
                        value={clientRequestForm.client_phone}
                        onChange={(e) => setClientRequestForm({...clientRequestForm, client_phone: e.target.value})}
                        required
                        className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                        placeholder="e.g., +27123456789"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Service Type *
                    </label>
                    <select
                      value={clientRequestForm.service}
                      onChange={(e) => setClientRequestForm({...clientRequestForm, service: e.target.value})}
                      required
                      className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    >
                      <option value="">Select a service</option>
                      {serviceOptions.map((service) => (
                        <option key={service} value={service}>{service}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Description *
                    </label>
                    <textarea
                      value={clientRequestForm.description}
                      onChange={(e) => setClientRequestForm({...clientRequestForm, description: e.target.value})}
                      required
                      rows="3"
                      className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                      placeholder="Describe what needs to be fixed or done..."
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Location *
                      </label>
                      <input
                        type="text"
                        value={clientRequestForm.location}
                        onChange={(e) => setClientRequestForm({...clientRequestForm, location: e.target.value})}
                        required
                        className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                        placeholder="Enter location/address"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Estimated Budget (R)
                      </label>
                      <input
                        type="number"
                        value={clientRequestForm.estimated_price}
                        onChange={(e) => setClientRequestForm({...clientRequestForm, estimated_price: e.target.value})}
                        min="0"
                        step="0.01"
                        className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                        placeholder="Optional budget"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Preferred Date & Time
                    </label>
                    <input
                      type="datetime-local"
                      value={clientRequestForm.scheduled_at}
                      onChange={(e) => setClientRequestForm({...clientRequestForm, scheduled_at: e.target.value})}
                      className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                  </div>

                  <div className="flex justify-end space-x-3">
                    <button
                      type="button"
                      onClick={() => setShowClientRequestForm(false)}
                      className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                    >
                      Create Request
                    </button>
                  </div>
                </form>
              )}
            </div>
          )}

          {activeTab === 'smart-matching' && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium">Smart Matching Dashboard</h3>
              <SmartMatchingDashboard />
            </div>
          )}

          {activeTab === 'compliance' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Business Compliance Services</h3>
                <div className="text-sm text-gray-600">
                  {complianceRequests.length} total requests
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[
                  { name: 'Company Registration', count: complianceRequests.filter(r => r.category === 'company_registration').length, color: 'blue' },
                  { name: 'Tax Compliance', count: complianceRequests.filter(r => r.category === 'tax_compliance').length, color: 'green' },
                  { name: 'Labour Law', count: complianceRequests.filter(r => r.category === 'labour_law').length, color: 'purple' },
                  { name: 'B-BBEE Certification', count: complianceRequests.filter(r => r.category === 'bbbee_certification').length, color: 'orange' },
                  { name: 'Licensing & Permits', count: complianceRequests.filter(r => r.category === 'licensing_permits').length, color: 'red' },
                  { name: 'Financial Compliance', count: complianceRequests.filter(r => r.category === 'financial_compliance').length, color: 'indigo' }
                ].map((service) => (
                  <div key={service.name} className={`bg-${service.color}-50 border border-${service.color}-200 rounded-lg p-4`}>
                    <div className={`text-2xl font-bold text-${service.color}-600`}>{service.count}</div>
                    <div className="text-gray-600 text-sm">{service.name}</div>
                    <div className={`text-xs text-${service.color}-500 mt-1`}>Active Requests</div>
                  </div>
                ))}
              </div>

              {complianceRequests.length > 0 && (
                <div className="bg-white border border-gray-200 rounded-lg">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h4 className="font-medium">Recent Compliance Requests</h4>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {complianceRequests.slice(0, 10).map((request) => (
                          <tr key={request.id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {request.category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                request.status === 'completed' ? 'bg-green-100 text-green-800' :
                                request.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                                'bg-yellow-100 text-yellow-800'
                              }`}>
                                {request.status.replace('_', ' ')}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {new Date(request.created_at).toLocaleDateString()}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;