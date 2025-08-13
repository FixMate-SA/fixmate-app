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
      
      // Update state with real data
      setEnterpriseData({
        bookings: overviewData.recent_bookings || [],
        contracts: [], // Will be added later if needed
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
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            New Bulk Booking
          </button>
        </div>
        
        <div className="mb-6">
          <h3 className="font-medium mb-3">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition-colors">
              <div className="text-center">
                <span className="text-3xl mb-2 block">🏢</span>
                <p className="font-medium">Property Maintenance</p>
                <p className="text-sm text-gray-600">Schedule recurring maintenance</p>
              </div>
            </button>
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition-colors">
              <div className="text-center">
                <span className="text-3xl mb-2 block">🧹</span>
                <p className="font-medium">Office Cleaning</p>
                <p className="text-sm text-gray-600">Book cleaning services</p>
              </div>
            </button>
            <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 transition-colors">
              <div className="text-center">
                <span className="text-3xl mb-2 block">🔧</span>
                <p className="font-medium">Emergency Repairs</p>
                <p className="text-sm text-gray-600">24/7 emergency support</p>
              </div>
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3">Service</th>
                <th className="text-left py-3">Location</th>
                <th className="text-left py-3">Date</th>
                <th className="text-left py-3">Status</th>
                <th className="text-left py-3">Actions</th>
              </tr>
            </thead>
            <tbody>
              {enterpriseData.bookings.map((booking) => (
                <tr key={booking.id} className="border-b">
                  <td className="py-3">{booking.service}</td>
                  <td className="py-3">{booking.location}</td>
                  <td className="py-3">{booking.date}</td>
                  <td className="py-3">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      booking.status === 'completed' ? 'bg-green-100 text-green-800' :
                      booking.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {booking.status}
                    </span>
                  </td>
                  <td className="py-3">
                    <button className="text-blue-600 hover:text-blue-800 mr-2">View</button>
                    <button className="text-green-600 hover:text-green-800">Edit</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderContracts = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Service Contracts</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            New Contract
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {enterpriseData.contracts.map((contract) => (
            <div key={contract.id} className="border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold">{contract.name}</h3>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  contract.status === 'active' ? 'bg-green-100 text-green-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {contract.status}
                </span>
              </div>
              <p className="text-gray-600 mb-2">Value: {formatCurrency(contract.value)}</p>
              <p className="text-sm text-gray-500">Renewal: {contract.renewal}</p>
              <div className="mt-4 flex space-x-2">
                <button className="text-blue-600 hover:text-blue-800 text-sm">View Details</button>
                <button className="text-green-600 hover:text-green-800 text-sm">Renew</button>
              </div>
            </div>
          ))}
        </div>
      </div>
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
            <p className="text-2xl font-bold text-blue-700">1,247</p>
            <p className="text-sm text-blue-500">+12% this month</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-green-600">Total Spend</h3>
            <p className="text-2xl font-bold text-green-700">R245,670</p>
            <p className="text-sm text-green-500">+8% this month</p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-purple-600">Active Locations</h3>
            <p className="text-2xl font-bold text-purple-700">24</p>
            <p className="text-sm text-purple-500">3 new this month</p>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <h3 className="text-sm font-medium text-orange-600">Cost Savings</h3>
            <p className="text-2xl font-bold text-orange-700">R52,340</p>
            <p className="text-sm text-orange-500">vs individual bookings</p>
          </div>
        </div>

        {/* Charts placeholder */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">📊 Service Usage Chart</p>
          </div>
          <div className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">📈 Cost Analysis Chart</p>
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
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Add Team Member
          </button>
        </div>
        
        {/* Team members list */}
        <div className="space-y-4">
          {[
            { name: 'John Manager', role: 'Account Manager', email: 'john@company.com', status: 'Active', permissions: 'Full Access' },
            { name: 'Sarah Supervisor', role: 'Site Supervisor', email: 'sarah@company.com', status: 'Active', permissions: 'Location Manager' },
            { name: 'Mike Facilities', role: 'Facilities Coordinator', email: 'mike@company.com', status: 'Active', permissions: 'Booking Only' }
          ].map((member, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-4">
                <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center text-white font-medium">
                  {member.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <h3 className="font-medium">{member.name}</h3>
                  <p className="text-sm text-gray-600">{member.role} • {member.email}</p>
                </div>
              </div>
              <div className="text-right">
                <span className="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full mb-1">
                  {member.status}
                </span>
                <p className="text-sm text-gray-500">{member.permissions}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderLocationManagement = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Location Management</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Add Location
          </button>
        </div>
        
        {/* Locations grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { name: 'Head Office', address: '123 Business District, Cape Town', active_bookings: 8, total_spend: 'R12,450' },
            { name: 'Warehouse North', address: '456 Industrial Ave, Johannesburg', active_bookings: 3, total_spend: 'R8,200' },
            { name: 'Branch Office', address: '789 Commerce St, Durban', active_bookings: 5, total_spend: 'R6,800' },
            { name: 'Factory East', address: '321 Manufacturing Rd, Port Elizabeth', active_bookings: 12, total_spend: 'R15,600' }
          ].map((location, index) => (
            <div key={index} className="p-4 border rounded-lg hover:bg-gray-50">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium">{location.name}</h3>
                <span className="text-2xl">📍</span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{location.address}</p>
              <div className="space-y-1">
                <div className="flex justify-between text-sm">
                  <span>Active Bookings:</span>
                  <span className="font-medium">{location.active_bookings}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Monthly Spend:</span>
                  <span className="font-medium text-green-600">{location.total_spend}</span>
                </div>
              </div>
              <div className="mt-3 flex space-x-2">
                <button className="text-blue-600 hover:text-blue-800 text-sm">Manage</button>
                <button className="text-green-600 hover:text-green-800 text-sm">Book Service</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderInvoicing = () => (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Enterprise Invoicing & Billing</h2>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Generate Invoice
          </button>
        </div>
        
        {/* Billing overview */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="p-4 bg-blue-50 rounded-lg">
            <h3 className="text-sm font-medium text-blue-600">Outstanding</h3>
            <p className="text-2xl font-bold text-blue-700">R18,450</p>
            <p className="text-sm text-blue-500">3 invoices pending</p>
          </div>
          <div className="p-4 bg-green-50 rounded-lg">
            <h3 className="text-sm font-medium text-green-600">Paid This Month</h3>
            <p className="text-2xl font-bold text-green-700">R67,890</p>
            <p className="text-sm text-green-500">12 invoices paid</p>
          </div>
          <div className="p-4 bg-purple-50 rounded-lg">
            <h3 className="text-sm font-medium text-purple-600">Next Billing</h3>
            <p className="text-2xl font-bold text-purple-700">R23,200</p>
            <p className="text-sm text-purple-500">Due in 5 days</p>
          </div>
        </div>

        {/* Recent invoices */}
        <div>
          <h3 className="font-medium mb-3">Recent Invoices</h3>
          <div className="space-y-3">
            {[
              { id: 'INV-2024-001', date: '2024-01-15', amount: 'R12,450', status: 'Paid', location: 'Head Office' },
              { id: 'INV-2024-002', date: '2024-01-10', amount: 'R8,200', status: 'Pending', location: 'Warehouse North' },
              { id: 'INV-2024-003', date: '2024-01-08', amount: 'R15,600', status: 'Overdue', location: 'Factory East' }
            ].map((invoice, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium">{invoice.id}</h4>
                  <p className="text-sm text-gray-600">{invoice.location} • {invoice.date}</p>
                </div>
                <div className="text-right">
                  <p className="font-medium">{invoice.amount}</p>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    invoice.status === 'Paid' ? 'bg-green-100 text-green-800' :
                    invoice.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {invoice.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
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