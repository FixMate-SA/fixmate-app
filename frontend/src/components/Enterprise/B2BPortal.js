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

  const analyticsData = {
    monthly_spend: 45000,
    jobs_completed: 156,
    average_rating: 4.8,
    cost_savings: 15000,
    response_time: '2.3 hours',
    completion_rate: 94
  };

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setEnterpriseData({
        bookings: [
          { id: 1, service: 'Office Cleaning', location: 'Sandton Office', date: '2024-01-20', status: 'completed' },
          { id: 2, service: 'HVAC Maintenance', location: 'Cape Town Branch', date: '2024-01-22', status: 'in_progress' },
          { id: 3, service: 'Electrical Repairs', location: 'Durban Store', date: '2024-01-25', status: 'scheduled' }
        ],
        contracts: [
          { id: 1, name: 'Property Management - Sandton', value: 150000, status: 'active', renewal: '2024-06-01' },
          { id: 2, name: 'Office Maintenance - Cape Town', value: 80000, status: 'active', renewal: '2024-04-15' }
        ],
        analytics: analyticsData,
        invoices: [
          { id: 1, amount: 25000, date: '2024-01-15', status: 'paid' },
          { id: 2, amount: 18000, date: '2024-01-01', status: 'pending' }
        ]
      });
      setLoading(false);
    }, 1000);
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