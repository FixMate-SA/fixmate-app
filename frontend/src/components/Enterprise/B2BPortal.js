import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import { apiService } from '../../services/api';

const B2BPortal = () => {
  const { user, roleInfo } = useAuth();
  const { t, formatCurrency } = useLanguage();
  const [activeTab, setActiveTab] = useState('overview');
  const [enterpriseData, setEnterpriseData] = useState({
    bookings: [],
    contracts: [],
    analytics: {},
    invoices: [],
    team: [],
    locations: []
  });
  const [loading, setLoading] = useState(true);
  const [showBulkBookingModal, setShowBulkBookingModal] = useState(false);
  const [showTeamMemberModal, setShowTeamMemberModal] = useState(false);
  const [showLocationModal, setShowLocationModal] = useState(false);
  const [showContractModal, setShowContractModal] = useState(false);
  const [newBulkBooking, setNewBulkBooking] = useState({
    services: [],
    locations: [],
    schedule_type: 'one-time',
    start_date: '',
    end_date: '',
    notes: ''
  });
  const [newTeamMember, setNewTeamMember] = useState({
    name: '',
    email: '',
    role: '',
    permissions: []
  });
  const [newLocation, setNewLocation] = useState({
    name: '',
    address: '',
    contact_person: '',
    contact_phone: '',
    services_needed: []
  });
  const [newContract, setNewContract] = useState({
    name: '',
    description: '',
    service_type: '',
    contract_value: '',
    duration_months: 12,
    start_date: '',
    auto_renewal: false,
    terms: ''
  });

  const tabs = [
    { id: 'overview', name: t('overview'), shortName: t('overview'), icon: '📊' },
    { id: 'bulk-bookings', name: t('bulkBookings', 'Bulk Bookings'), shortName: t('bookings', 'Bookings'), icon: '📋' },
    { id: 'contracts', name: t('contracts'), shortName: t('contracts'), icon: '📄' },
    { id: 'analytics', name: t('analytics'), shortName: t('analytics'), icon: '📈' },
    { id: 'team', name: t('teamManagement', 'Team Management'), shortName: t('team', 'Team'), icon: '👥' },
    { id: 'locations', name: t('locationManagement', 'Locations'), shortName: t('locations', 'Locations'), icon: '📍' },
    { id: 'invoicing', name: t('invoicing'), shortName: t('invoicing'), icon: '💰' },
    { id: 'settings', name: t('settings'), shortName: t('settings'), icon: '⚙️' }
  ];

  const servicePackages = [
    {
      id: 'property_management',
      name: 'Property Management',
      description: 'Complete property maintenance solutions',
      features: [
        'Scheduled maintenance',
        'Emergency repairs',
        'Compliance reporting',
        'Tenant communication',
        'Cost tracking'
      ],
      price: 'From R2,500/month per property'
    },
    {
      id: 'office_maintenance',
      name: 'Office Maintenance',
      description: 'Comprehensive office facility management',
      features: [
        'Daily cleaning',
        'IT support',
        'Electrical maintenance',
        'HVAC servicing',
        'Security system checks'
      ],
      price: 'From R5,000/month per office'
    },
    {
      id: 'retail_support',
      name: 'Retail Support',
      description: 'Specialized retail facility services',
      features: [
        'Store maintenance',
        'Display repairs',
        'Lighting management',
        'Safety compliance',
        'Emergency response'
      ],
      price: 'From R3,500/month per store'
    },
    {
      id: 'hospitality',
      name: 'Hospitality Services',
      description: 'Hotel and restaurant maintenance',
      features: [
        'Room maintenance',
        'Kitchen equipment',
        'Guest area upkeep',
        'Compliance audits',
        '24/7 support'
      ],
      price: 'From R8,000/month per venue'
    }
  ];

  // Get analytics data from state instead of hardcoded
  const analyticsData = enterpriseData.analytics || {
    monthly_spend: 0,
    jobs_completed: 0,
    cost_savings: 0,
    response_time: '2.3 hours',
    completion_rate: 94,
    customer_satisfaction: 4.8
  };

  const fetchEnterpriseData = async () => {
    try {
      setLoading(true);
      console.log('🏢 Fetching enterprise data...');
      
      const token = localStorage.getItem('fixmate_token');
      const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };
      
      // Fetch overview data
      const overviewResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/overview`, { headers });
      let overviewData = {};
      if (overviewResponse.ok) {
        const overview = await overviewResponse.json();
        overviewData = overview.success ? overview.data : {};
      }
      
      // Fetch team members
      const teamResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/team`, { headers });
      let teamData = [];
      if (teamResponse.ok) {
        const team = await teamResponse.json();
        teamData = team.success ? team.team_members : [];
      }
      
      // Fetch locations
      const locationsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/locations`, { headers });
      let locationsData = [];
      if (locationsResponse.ok) {
        const locations = await locationsResponse.json();
        locationsData = locations.success ? locations.locations : [];
      }
      
      // Fetch invoices
      const invoicesResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/invoices`, { headers });
      let invoicesData = [];
      if (invoicesResponse.ok) {
        const invoices = await invoicesResponse.json();
        invoicesData = invoices.success ? invoices.invoices : [];
      }
      
      // Fetch contracts
      const contractsResponse = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/contracts`, { headers });
      let contractsData = [];
      if (contractsResponse.ok) {
        const contracts = await contractsResponse.json();
        contractsData = contracts.success ? contracts.contracts : [];
      }
      
      // Update state with real data
      setEnterpriseData({
        bookings: overviewData.recent_bookings || [],
        contracts: contractsData,
        analytics: overviewData.analytics || {},
        invoices: invoicesData,
        team: teamData,
        locations: locationsData
      });
      
      console.log('✅ Enterprise data loaded successfully');
      
    } catch (error) {
      console.error('❌ Error fetching enterprise data:', error);
      // Keep default empty data on error
    } finally {
      setLoading(false);
    }
  };

  // Bulk booking handlers
  const handleCreateBulkBooking = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/bulk-booking`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newBulkBooking)
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert('✅ Bulk booking created successfully!');
          setShowBulkBookingModal(false);
          fetchEnterpriseData(); // Refresh data
          // Reset form
          setNewBulkBooking({
            services: [],
            locations: [],
            schedule_type: 'one-time',
            start_date: '',
            end_date: '',
            notes: ''
          });
        } else {
          alert(`❌ Error: ${result.message}`);
        }
      } else {
        alert('❌ Failed to create bulk booking. Please try again.');
      }
    } catch (error) {
      console.error('Bulk booking error:', error);
      alert('❌ Error creating bulk booking. Please try again.');
    }
  };

  // Team management handlers
  const handleAddTeamMember = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/team`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newTeamMember)
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert('✅ Team member added successfully!');
          setShowTeamMemberModal(false);
          fetchEnterpriseData(); // Refresh data
          // Reset form
          setNewTeamMember({
            name: '',
            email: '',
            role: '',
            permissions: []
          });
        } else {
          alert(`❌ Error: ${result.message}`);
        }
      } else {
        alert('❌ Failed to add team member. Please try again.');
      }
    } catch (error) {
      console.error('Add team member error:', error);
      alert('❌ Error adding team member. Please try again.');
    }
  };

  const handleRemoveTeamMember = async (memberId) => {
    if (!window.confirm('Are you sure you want to remove this team member?')) {
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/team/${memberId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert('✅ Team member removed successfully!');
          fetchEnterpriseData(); // Refresh data
        } else {
          alert(`❌ Error: ${result.message}`);
        }
      } else {
        alert('❌ Failed to remove team member. Please try again.');
      }
    } catch (error) {
      console.error('Remove team member error:', error);
      alert('❌ Error removing team member. Please try again.');
    }
  };

  // Location management handlers
  const handleAddLocation = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/locations`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newLocation)
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert('✅ Location added successfully!');
          setShowLocationModal(false);
          fetchEnterpriseData(); // Refresh data
          // Reset form
          setNewLocation({
            name: '',
            address: '',
            contact_person: '',
            contact_phone: '',
            services_needed: []
          });
        } else {
          alert(`❌ Error: ${result.message}`);
        }
      } else {
        alert('❌ Failed to add location. Please try again.');
      }
    } catch (error) {
      console.error('Add location error:', error);
      alert('❌ Error adding location. Please try again.');
    }
  };

  const handleRemoveLocation = async (locationId) => {
    if (!window.confirm('Are you sure you want to remove this location?')) {
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/locations/${locationId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert('✅ Location removed successfully!');
          fetchEnterpriseData(); // Refresh data
        } else {
          alert(`❌ Error: ${result.message}`);
        }
      } else {
        alert('❌ Failed to remove location. Please try again.');
      }
    } catch (error) {
      console.error('Remove location error:', error);
      alert('❌ Error removing location. Please try again.');
    }
  };

  const handleBookServiceForLocation = async (locationId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/locations/${locationId}/book-service`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert('✅ Service booked successfully for location!');
          fetchEnterpriseData(); // Refresh data
        } else {
          alert(`❌ Error: ${result.message}`);
        }
      } else {
        alert('❌ Failed to book service. Please try again.');
      }
    } catch (error) {
      console.error('Book service error:', error);
      alert('❌ Error booking service. Please try again.');
    }
  };

  // Invoice generation
  const handleGenerateInvoice = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/generate-invoice`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert(`✅ Invoice generated successfully! Total: R${result.invoice.total_amount}`);
          fetchEnterpriseData(); // Refresh data
        } else {
          alert(`❌ Error: ${result.message}`);
        }
      } else {
        alert('❌ Failed to generate invoice. Please try again.');
      }
    } catch (error) {
      console.error('Generate invoice error:', error);
      alert('❌ Error generating invoice. Please try again.');
    }
  };

  // Contract management handlers
  const handleAddContract = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/contracts`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(newContract)
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert('✅ Contract added successfully!');
          setShowContractModal(false);
          fetchEnterpriseData(); // Refresh data
          // Reset form
          setNewContract({
            name: '',
            description: '',
            service_type: '',
            contract_value: '',
            duration_months: 12,
            start_date: '',
            auto_renewal: false,
            terms: ''
          });
        } else {
          alert(`❌ Error: ${result.message}`);
        }
      } else {
        alert('❌ Failed to add contract. Please try again.');
      }
    } catch (error) {
      console.error('Add contract error:', error);
      alert('❌ Error adding contract. Please try again.');
    }
  };

  const handleRemoveContract = async (contractId) => {
    if (!window.confirm('Are you sure you want to remove this contract?')) {
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/contracts/${contractId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert('✅ Contract removed successfully!');
          fetchEnterpriseData(); // Refresh data
        } else {
          alert(`❌ Error: ${result.message}`);
        }
      } else {
        alert('❌ Failed to remove contract. Please try again.');
      }
    } catch (error) {
      console.error('Remove contract error:', error);
      alert('❌ Error removing contract. Please try again.');
    }
  };

  const handleRenewContract = async (contractId) => {
    if (!window.confirm('Are you sure you want to renew this contract?')) {
      return;
    }
    
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/enterprise/contracts/${contractId}/renew`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          alert(`✅ Contract renewed successfully! New end date: ${result.new_end_date}`);
          fetchEnterpriseData(); // Refresh data
        } else {
          alert(`❌ Error: ${result.message}`);
        }
      } else {
        alert('❌ Failed to renew contract. Please try again.');
      }
    } catch (error) {
      console.error('Renew contract error:', error);
      alert('❌ Error renewing contract. Please try again.');
    }
  };

  useEffect(() => {
    fetchEnterpriseData();
  }, []);

  const renderOverview = () => (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-full">
              <span className="text-2xl">💰</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Monthly Spend</p>
              <p className="text-2xl font-bold">{formatCurrency(analyticsData.monthly_spend)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-full">
              <span className="text-2xl">✅</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Jobs Completed</p>
              <p className="text-2xl font-bold">{analyticsData.jobs_completed}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-full">
              <span className="text-2xl">⭐</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Average Rating</p>
              <p className="text-2xl font-bold">{analyticsData.average_rating}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-full">
              <span className="text-2xl">💸</span>
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">Cost Savings</p>
              <p className="text-2xl font-bold">{formatCurrency(analyticsData.cost_savings)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Service Packages */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold mb-4">Enterprise Service Packages</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {servicePackages.map((pkg) => (
            <div key={pkg.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <h3 className="font-semibold text-lg mb-2">{pkg.name}</h3>
              <p className="text-gray-600 mb-4">{pkg.description}</p>
              <ul className="space-y-2 mb-4">
                {pkg.features.map((feature, index) => (
                  <li key={index} className="flex items-center text-sm">
                    <span className="text-green-500 mr-2">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
              <div className="flex items-center justify-between">
                <span className="text-blue-600 font-semibold">{pkg.price}</span>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                  Learn More
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {enterpriseData.bookings.slice(0, 3).map((booking) => (
            <div key={booking.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-md">
              <div>
                <h3 className="font-medium">{booking.service}</h3>
                <p className="text-sm text-gray-600">{booking.location}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">{booking.date}</p>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  booking.status === 'completed' ? 'bg-green-100 text-green-800' :
                  booking.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {booking.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderBulkBookings = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Bulk Service Bookings</h2>
          <button 
            onClick={() => setShowBulkBookingModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            New Bulk Booking
          </button>
        </div>
        
        <div className="mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-blue-600 font-medium">Active Bookings</p>
              <p className="text-2xl font-bold text-blue-800">{enterpriseData.bookings.length}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-green-600 font-medium">This Month</p>
              <p className="text-2xl font-bold text-green-800">R{formatCurrency(analyticsData.monthly_spend)}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-purple-600 font-medium">Cost Savings</p>
              <p className="text-2xl font-bold text-purple-800">R{formatCurrency(analyticsData.cost_savings)}</p>
            </div>
          </div>
        </div>
        
        {/* Recent Bookings */}
        <div>
          <h3 className="font-medium mb-3">Recent Bulk Bookings</h3>
          {enterpriseData.bookings.length > 0 ? (
            <div className="space-y-3">
              {enterpriseData.bookings.map((booking, index) => (
                <div key={booking.id || index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{booking.services ? booking.services.join(', ') : 'Multiple Services'}</p>
                      <p className="text-sm text-gray-600">{booking.locations ? booking.locations.join(', ') : booking.location || 'Multiple Locations'}</p>
                      <p className="text-xs text-gray-500">
                        {booking.schedule_type} • {booking.start_date || booking.date}
                      </p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      booking.status === 'active' ? 'bg-green-100 text-green-800' :
                      booking.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                      booking.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {booking.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No bulk bookings yet. Create your first bulk booking to get started!</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Bulk Booking Modal */}
      {showBulkBookingModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-semibold mb-4">Create Bulk Booking</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Services (comma-separated)</label>
                <input
                  type="text"
                  value={newBulkBooking.services.join(', ')}
                  onChange={(e) => setNewBulkBooking({
                    ...newBulkBooking,
                    services: e.target.value.split(',').map(s => s.trim())
                  })}
                  className="w-full p-2 border rounded-md"
                  placeholder="Cleaning, Maintenance, Repairs"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Locations (comma-separated)</label>
                <input
                  type="text"
                  value={newBulkBooking.locations.join(', ')}
                  onChange={(e) => setNewBulkBooking({
                    ...newBulkBooking,
                    locations: e.target.value.split(',').map(l => l.trim())
                  })}
                  className="w-full p-2 border rounded-md"
                  placeholder="Office A, Office B, Warehouse"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Schedule Type</label>
                <select
                  value={newBulkBooking.schedule_type}
                  onChange={(e) => setNewBulkBooking({...newBulkBooking, schedule_type: e.target.value})}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="one-time">One-time</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Start Date</label>
                <input
                  type="date"
                  value={newBulkBooking.start_date}
                  onChange={(e) => setNewBulkBooking({...newBulkBooking, start_date: e.target.value})}
                  className="w-full p-2 border rounded-md"
                />
              </div>
              
              {newBulkBooking.schedule_type !== 'one-time' && (
                <div>
                  <label className="block text-sm font-medium mb-2">End Date</label>
                  <input
                    type="date"
                    value={newBulkBooking.end_date}
                    onChange={(e) => setNewBulkBooking({...newBulkBooking, end_date: e.target.value})}
                    className="w-full p-2 border rounded-md"
                  />
                </div>
              )}
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleCreateBulkBooking}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
              >
                Create Booking
              </button>
              <button
                onClick={() => setShowBulkBookingModal(false)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderContracts = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Service Contracts</h2>
          <button 
            onClick={() => setShowContractModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            New Contract
          </button>
        </div>

        {enterpriseData.contracts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {enterpriseData.contracts.map((contract) => (
              <div key={contract.id} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold">{contract.name}</h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    contract.status === 'active' ? 'bg-green-100 text-green-800' :
                    contract.status === 'expired' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {contract.status}
                  </span>
                </div>
                <p className="text-gray-600 mb-2">{contract.description}</p>
                <p className="text-gray-600 mb-2">Value: {formatCurrency(contract.value)}</p>
                <p className="text-sm text-gray-500">Service: {contract.service_type}</p>
                <p className="text-sm text-gray-500">
                  Duration: {contract.duration_months} months
                </p>
                <p className="text-sm text-gray-500">
                  Period: {new Date(contract.start_date).toLocaleDateString()} - {new Date(contract.end_date).toLocaleDateString()}
                </p>
                {contract.auto_renewal && (
                  <p className="text-sm text-green-600">Auto-renewal enabled</p>
                )}
                <div className="mt-4 flex space-x-2">
                  <button className="text-blue-600 hover:text-blue-800 text-sm">View Details</button>
                  <button 
                    onClick={() => handleRenewContract(contract.id)}
                    className="text-green-600 hover:text-green-800 text-sm"
                  >
                    Renew
                  </button>
                  <button
                    onClick={() => handleRemoveContract(contract.id)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>No contracts created yet. Add your first contract to manage enterprise services!</p>
            <button 
              onClick={() => setShowContractModal(true)}
              className="mt-3 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Create First Contract
            </button>
          </div>
        )}
      </div>
      
      {/* Contract Modal */}
      {showContractModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-semibold mb-4">New Contract</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Contract Name</label>
                <input
                  type="text"
                  value={newContract.name}
                  onChange={(e) => setNewContract({...newContract, name: e.target.value})}
                  className="w-full p-2 border rounded-md"
                  placeholder="Annual Maintenance Contract"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  value={newContract.description}
                  onChange={(e) => setNewContract({...newContract, description: e.target.value})}
                  className="w-full p-2 border rounded-md"
                  rows="3"
                  placeholder="Comprehensive facility management services..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Service Type</label>
                <select
                  value={newContract.service_type}
                  onChange={(e) => setNewContract({...newContract, service_type: e.target.value})}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="">Select Service Type</option>
                  <option value="Property Management">Property Management</option>
                  <option value="Office Maintenance">Office Maintenance</option>
                  <option value="Retail Support">Retail Support</option>
                  <option value="Hospitality Services">Hospitality Services</option>
                  <option value="IT Support">IT Support</option>
                  <option value="Security Services">Security Services</option>
                  <option value="Cleaning Services">Cleaning Services</option>
                </select>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Contract Value (R)</label>
                  <input
                    type="number"
                    value={newContract.contract_value}
                    onChange={(e) => setNewContract({...newContract, contract_value: e.target.value})}
                    className="w-full p-2 border rounded-md"
                    placeholder="50000"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Duration (Months)</label>
                  <input
                    type="number"
                    value={newContract.duration_months}
                    onChange={(e) => setNewContract({...newContract, duration_months: parseInt(e.target.value)})}
                    className="w-full p-2 border rounded-md"
                    placeholder="12"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Start Date</label>
                <input
                  type="date"
                  value={newContract.start_date}
                  onChange={(e) => setNewContract({...newContract, start_date: e.target.value})}
                  className="w-full p-2 border rounded-md"
                />
              </div>
              
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newContract.auto_renewal}
                    onChange={(e) => setNewContract({...newContract, auto_renewal: e.target.checked})}
                    className="mr-2"
                  />
                  <span className="text-sm">Enable automatic renewal</span>
                </label>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Terms & Conditions (Optional)</label>
                <textarea
                  value={newContract.terms}
                  onChange={(e) => setNewContract({...newContract, terms: e.target.value})}
                  className="w-full p-2 border rounded-md"
                  rows="3"
                  placeholder="Additional terms and conditions..."
                />
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleAddContract}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
              >
                Create Contract
              </button>
              <button
                onClick={() => setShowContractModal(false)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderAnalytics = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold mb-4">Enterprise Analytics Dashboard</h2>
        
        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-blue-600">Total Bookings</h3>
            <p className="text-2xl font-bold text-blue-700">{enterpriseData.bookings.length}</p>
            <p className="text-sm text-blue-500">+{Math.floor(enterpriseData.bookings.length * 0.12)} this month</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-green-600">Total Spend</h3>
            <p className="text-2xl font-bold text-green-700">R{formatCurrency(analyticsData.monthly_spend)}</p>
            <p className="text-sm text-green-500">+8% this month</p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-purple-600">Active Locations</h3>
            <p className="text-2xl font-bold text-purple-700">{enterpriseData.locations.length}</p>
            <p className="text-sm text-purple-500">{Math.max(1, Math.floor(enterpriseData.locations.length * 0.3))} new this month</p>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-orange-600">Cost Savings</h3>
            <p className="text-2xl font-bold text-orange-700">R{formatCurrency(analyticsData.cost_savings)}</p>
            <p className="text-sm text-orange-500">vs individual bookings</p>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium mb-2">Team Performance</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Active Team Members:</span>
                <span className="font-medium">{enterpriseData.team.length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Average Rating:</span>
                <span className="font-medium">{analyticsData.customer_satisfaction || 4.8}/5.0</span>
              </div>
            </div>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-medium mb-2">Financial Summary</h4>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Total Invoices:</span>
                <span className="font-medium">{enterpriseData.invoices.length}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Completion Rate:</span>
                <span className="font-medium">{analyticsData.completion_rate || 94}%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Charts placeholder */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <p className="text-gray-500 text-lg">📊 Service Usage Chart</p>
              <p className="text-sm text-gray-400 mt-2">
                Bookings: {enterpriseData.bookings.length} | Locations: {enterpriseData.locations.length}
              </p>
            </div>
          </div>
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <p className="text-gray-500 text-lg">📈 Cost Analysis Chart</p>
              <p className="text-sm text-gray-400 mt-2">
                Monthly Spend: R{formatCurrency(analyticsData.monthly_spend)}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTeamManagement = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Team Management</h2>
          <button 
            onClick={() => setShowTeamMemberModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Add Team Member
          </button>
        </div>
        
        {/* Team members list */}
        <div className="space-y-4">
          {enterpriseData.team.length > 0 ? (
            enterpriseData.team.map((member) => (
              <div key={member.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                    {member.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <h3 className="font-medium">{member.name}</h3>
                    <p className="text-sm text-gray-600">{member.role} • {member.email}</p>
                  </div>
                </div>
                <div className="text-right flex items-center space-x-3">
                  <div>
                    <span className="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full mb-1">
                      Active
                    </span>
                    <p className="text-sm text-gray-500">{member.permissions ? member.permissions.join(', ') : 'Basic Access'}</p>
                  </div>
                  <button
                    onClick={() => handleRemoveTeamMember(member.id)}
                    className="text-red-600 hover:text-red-800 text-sm px-2 py-1 rounded"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No team members added yet. Add your first team member to manage enterprise services!</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Team Member Modal */}
      {showTeamMemberModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-semibold mb-4">Add Team Member</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Name</label>
                <input
                  type="text"
                  value={newTeamMember.name}
                  onChange={(e) => setNewTeamMember({...newTeamMember, name: e.target.value})}
                  className="w-full p-2 border rounded-md"
                  placeholder="John Doe"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <input
                  type="email"
                  value={newTeamMember.email}
                  onChange={(e) => setNewTeamMember({...newTeamMember, email: e.target.value})}
                  className="w-full p-2 border rounded-md"
                  placeholder="john@company.com"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Role</label>
                <select
                  value={newTeamMember.role}
                  onChange={(e) => setNewTeamMember({...newTeamMember, role: e.target.value})}
                  className="w-full p-2 border rounded-md"
                >
                  <option value="">Select Role</option>
                  <option value="Account Manager">Account Manager</option>
                  <option value="Site Supervisor">Site Supervisor</option>
                  <option value="Facilities Coordinator">Facilities Coordinator</option>
                  <option value="Team Lead">Team Lead</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Permissions (comma-separated)</label>
                <input
                  type="text"
                  value={newTeamMember.permissions.join(', ')}
                  onChange={(e) => setNewTeamMember({
                    ...newTeamMember, 
                    permissions: e.target.value.split(',').map(p => p.trim())
                  })}
                  className="w-full p-2 border rounded-md"
                  placeholder="Full Access, Location Manager, Booking Only"
                />
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleAddTeamMember}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
              >
                Add Member
              </button>
              <button
                onClick={() => setShowTeamMemberModal(false)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderLocationManagement = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Location Management</h2>
          <button 
            onClick={() => setShowLocationModal(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Add Location
          </button>
        </div>
        
        {/* Locations grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {enterpriseData.locations.length > 0 ? (
            enterpriseData.locations.map((location) => (
              <div key={location.id} className="p-4 border rounded-lg hover:bg-gray-50">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="font-medium">{location.name}</h3>
                  <span className="text-2xl">📍</span>
                </div>
                <p className="text-sm text-gray-600 mb-3">{location.address}</p>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>Contact:</span>
                    <span className="font-medium">{location.contact_person}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Phone:</span>
                    <span className="font-medium">{location.contact_phone}</span>
                  </div>
                  {location.services_needed && location.services_needed.length > 0 && (
                    <div className="mt-2">
                      <span className="text-sm text-gray-500">Services: </span>
                      <span className="text-sm">{location.services_needed.join(', ')}</span>
                    </div>
                  )}
                </div>
                <div className="mt-3 flex space-x-2">
                  <button className="text-blue-600 hover:text-blue-800 text-sm">Manage</button>
                  <button 
                    onClick={() => handleBookServiceForLocation(location.id)}
                    className="text-green-600 hover:text-green-800 text-sm"
                  >
                    Book Service
                  </button>
                  <button
                    onClick={() => handleRemoveLocation(location.id)}
                    className="text-red-600 hover:text-red-800 text-sm"
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full text-center py-8 text-gray-500">
              <p>No locations added yet. Add your first location to manage enterprise services!</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Location Modal */}
      {showLocationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-xl font-semibold mb-4">Add Location</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Location Name</label>
                <input
                  type="text"
                  value={newLocation.name}
                  onChange={(e) => setNewLocation({...newLocation, name: e.target.value})}
                  className="w-full p-2 border rounded-md"
                  placeholder="Head Office"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Address</label>
                <input
                  type="text"
                  value={newLocation.address}
                  onChange={(e) => setNewLocation({...newLocation, address: e.target.value})}
                  className="w-full p-2 border rounded-md"
                  placeholder="123 Business District, Cape Town"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Contact Person</label>
                <input
                  type="text"
                  value={newLocation.contact_person}
                  onChange={(e) => setNewLocation({...newLocation, contact_person: e.target.value})}
                  className="w-full p-2 border rounded-md"
                  placeholder="John Manager"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Contact Phone</label>
                <input
                  type="tel"
                  value={newLocation.contact_phone}
                  onChange={(e) => setNewLocation({...newLocation, contact_phone: e.target.value})}
                  className="w-full p-2 border rounded-md"
                  placeholder="+27 11 123 4567"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Services Needed (comma-separated)</label>
                <input
                  type="text"
                  value={newLocation.services_needed.join(', ')}
                  onChange={(e) => setNewLocation({
                    ...newLocation, 
                    services_needed: e.target.value.split(',').map(s => s.trim())
                  })}
                  className="w-full p-2 border rounded-md"
                  placeholder="Cleaning, Maintenance, Security"
                />
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleAddLocation}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
              >
                Add Location
              </button>
              <button
                onClick={() => setShowLocationModal(false)}
                className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderInvoicing = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Enterprise Invoicing & Billing</h2>
          <button 
            onClick={handleGenerateInvoice}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Generate Invoice
          </button>
        </div>
        
        {/* Billing overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="p-4 bg-blue-50 rounded-lg">
            <h3 className="text-sm font-medium text-blue-600">Outstanding</h3>
            <p className="text-2xl font-bold text-blue-700">
              R{formatCurrency(
                enterpriseData.invoices
                  .filter(inv => inv.status === 'pending' || inv.status === 'overdue')
                  .reduce((sum, inv) => sum + inv.amount, 0)
              )}
            </p>
            <p className="text-sm text-blue-500">
              {enterpriseData.invoices.filter(inv => inv.status === 'pending' || inv.status === 'overdue').length} invoices pending
            </p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <h3 className="text-sm font-medium text-green-600">Paid This Month</h3>
            <p className="text-2xl font-bold text-green-700">
              R{formatCurrency(
                enterpriseData.invoices
                  .filter(inv => inv.status === 'paid')
                  .reduce((sum, inv) => sum + inv.amount, 0)
              )}
            </p>
            <p className="text-sm text-green-500">
              {enterpriseData.invoices.filter(inv => inv.status === 'paid').length} invoices paid
            </p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <h3 className="text-sm font-medium text-purple-600">Total Invoices</h3>
            <p className="text-2xl font-bold text-purple-700">{enterpriseData.invoices.length}</p>
            <p className="text-sm text-purple-500">
              R{formatCurrency(
                enterpriseData.invoices.reduce((sum, inv) => sum + inv.amount, 0)
              )} total value
            </p>
          </div>
        </div>

        {/* Recent invoices */}
        <div>
          <h3 className="font-medium mb-3">Recent Invoices</h3>
          {enterpriseData.invoices.length > 0 ? (
            <div className="space-y-3">
              {enterpriseData.invoices.slice(0, 5).map((invoice) => (
                <div key={invoice.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-medium">{invoice.invoice_number}</h4>
                    <p className="text-sm text-gray-600">
                      {invoice.description || 'Enterprise Services'} • {new Date(invoice.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">R{formatCurrency(invoice.amount)}</p>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      invoice.status === 'paid' ? 'bg-green-100 text-green-800' :
                      invoice.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      invoice.status === 'overdue' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {invoice.status}
                    </span>
                  </div>
                </div>
              ))}
              {enterpriseData.invoices.length > 5 && (
                <div className="text-center py-2">
                  <button className="text-blue-600 hover:text-blue-800 text-sm">
                    View All Invoices ({enterpriseData.invoices.length})
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <p>No invoices generated yet. Generate your first invoice to get started!</p>
              <button 
                onClick={handleGenerateInvoice}
                className="mt-3 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Generate First Invoice
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold mb-4">Enterprise Settings</h2>
        
        <div className="space-y-6">
          {/* Company Information */}
          <div>
            <h3 className="font-medium mb-3">Company Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                <input type="text" defaultValue="FixMate Enterprise Client" className="w-full border rounded-md px-3 py-2" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Industry</label>
                <select className="w-full border rounded-md px-3 py-2">
                  <option>Property Management</option>
                  <option>Facilities Management</option>
                  <option>Corporate Services</option>
                  <option>Retail</option>
                </select>
              </div>
            </div>
          </div>

          {/* Billing Preferences */}
          <div>
            <h3 className="font-medium mb-3">Billing Preferences</h3>
            <div className="space-y-3">
              <label className="flex items-center">
                <input type="radio" name="billing" defaultChecked className="mr-2" />
                <span>Monthly consolidated invoicing</span>
              </label>
              <label className="flex items-center">
                <input type="radio" name="billing" className="mr-2" />
                <span>Per-location billing</span>
              </label>
              <label className="flex items-center">
                <input type="radio" name="billing" className="mr-2" />
                <span>Per-service billing</span>
              </label>
            </div>
          </div>

          {/* Notification Preferences */}
          <div>
            <h3 className="font-medium mb-3">Notification Preferences</h3>
            <div className="space-y-3">
              <label className="flex items-center">
                <input type="checkbox" defaultChecked className="mr-2" />
                <span>Email notifications for completed services</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" defaultChecked className="mr-2" />
                <span>SMS alerts for urgent issues</span>
              </label>
              <label className="flex items-center">
                <input type="checkbox" className="mr-2" />
                <span>Weekly analytics reports</span>
              </label>
            </div>
          </div>

          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6 mb-6">
        <h1 className="text-3xl font-bold mb-2">Enterprise Portal</h1>
        <p className="text-blue-100">
          Comprehensive business solutions for property management, facilities, and corporate accounts
        </p>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow-sm border mb-6">
        <div className="flex overflow-x-auto scrollbar-hide p-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-md transition-colors whitespace-nowrap flex-shrink-0 ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <span className="text-lg">{tab.icon}</span>
              <span className="font-medium hidden sm:inline">{tab.name}</span>
              <span className="font-medium sm:hidden">{tab.shortName}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'bulk-bookings' && renderBulkBookings()}
        {activeTab === 'contracts' && renderContracts()}
        {activeTab === 'analytics' && renderAnalytics()}
        {activeTab === 'team' && renderTeamManagement()}
        {activeTab === 'locations' && renderLocationManagement()}
        {activeTab === 'invoicing' && renderInvoicing()}
        {activeTab === 'settings' && renderSettings()}
      </div>
    </div>
  );
};

export default B2BPortal;