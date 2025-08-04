import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/api';
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

      // Create the job request
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

      const response = await fetch(`${API_BASE_URL}/jobs/workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jobData)
      });

      if (response.ok) {
        const responseData = await response.json();
        alert(`Service request created successfully for ${clientRequestForm.client_name}! Job ID: ${responseData.job_id}`);
        
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
        const errorData = await response.json();
        alert(`Failed to create service request: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error creating client service request:', error);
      alert('Failed to create service request');
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
          <div className="text-gray-600">Total Users</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-3xl font-bold text-orange-600">{stats.totalFixers}</div>
          <div className="text-gray-600">Total Fixers</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-3xl font-bold text-emerald-600">{stats.activeFixers}</div>
          <div className="text-gray-600">Active Fixers</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-3xl font-bold text-red-600">{stats.inactiveFixers}</div>
          <div className="text-gray-600">Inactive Fixers</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow-sm">
          <div className="text-3xl font-bold text-yellow-600">{stats.avgFixerRating}⭐</div>
          <div className="text-gray-600">Avg Rating</div>
        </div>
      </div>

      {/* Admin Tabs */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-2 md:space-x-8 px-2 md:px-6 overflow-x-auto">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'client-request', label: 'Client Request', icon: '📞' },
              { id: 'smart-matching', label: 'Smart Matching', icon: '🎯' },
              { id: 'compliance', label: 'Compliance', icon: '🏢' },
              { id: 'fixers', label: 'Fixer Mgmt', icon: '🔧' },
              { id: 'payments', label: 'Payments', icon: '💳' },
              { id: 'users', label: 'Users', icon: '👥' },
              { id: 'reports', label: 'Reports', icon: '📈' }
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

          {activeTab === 'fixers' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-medium">Fixer Management</h3>
                <div className="text-sm text-gray-600">
                  {fixers.length} total fixers
                </div>
              </div>
              
              <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 md:rounded-lg">
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Services</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rating</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {fixers.map((fixer) => (
                      <tr key={fixer.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {fixer.name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {fixer.phone}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">
                          <div className="max-w-xs">
                            {JSON.parse(fixer.services).slice(0, 2).map((service, i) => (
                              <span key={i} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-1 mb-1">
                                {service}
                              </span>
                            ))}
                            {JSON.parse(fixer.services).length > 2 && (
                              <span className="text-xs text-gray-500">+{JSON.parse(fixer.services).length - 2} more</span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {fixer.rating.toFixed(1)}⭐ ({fixer.total_jobs} jobs)
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            fixer.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {fixer.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <button
                            onClick={() => setSelectedFixer(fixer)}
                            className="text-red-600 hover:text-red-900 font-medium"
                          >
                            Manage Payments
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
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
                <table className="min-w-full divide-y divide-gray-300">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Phone</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID Number</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {users.map((user) => (
                      <tr key={user.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {user.first_name && user.last_name 
                            ? `${user.first_name} ${user.last_name}`.trim()
                            : user.first_name || user.last_name || 'No Name'
                          }
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {user.phone}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {user.id_number || 'Not provided'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            user.role === 'admin' ? 'bg-red-100 text-red-800' :
                            user.role === 'fixer' ? 'bg-orange-100 text-orange-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {user.role?.charAt(0)?.toUpperCase() + user.role?.slice(1)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            user.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
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
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;