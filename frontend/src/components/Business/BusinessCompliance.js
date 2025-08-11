import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';

const BusinessCompliance = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('categories');
  const [categories, setCategories] = useState({});
  const [userRequests, setUserRequests] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [requestForm, setRequestForm] = useState({
    category: '',
    description: '',
    urgency_level: 'normal',
    contact_preference: 'whatsapp'
  });
  const [checklist, setChecklist] = useState(null);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchCategories();
    fetchUserRequests();
  }, []);

  const fetchCategories = async () => {
    try {
      const apiUrl = process.env.REACT_APP_BACKEND_URL || '/api';
      const response = await fetch(`${apiUrl}/api/compliance/categories`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setCategories(data);
      console.log('✅ Business compliance categories loaded:', Object.keys(data).length);
    } catch (error) {
      console.error('❌ Error fetching business compliance categories:', error);
      // Set fallback categories if API fails - role-based services
      const getRoleBasedCategories = () => {
        const userRole = user?.role_info?.role || 'client';
        
        if (userRole === 'fixer') {
          return {
            professional_licensing: {
              name: 'Professional Licensing',
              description: 'Electrical, plumbing, construction, and trade-specific licenses',
              cost_range: 'R800 - R2,500',
              processing_time: '15-30 business days'
            },
            business_registration: {
              name: 'Business Fixer Registration',
              description: 'Register as sole proprietor, CC, or Pty Ltd for fixer services',
              cost_range: 'R1,200 - R3,500',
              processing_time: '10-15 business days'
            },
            tax_compliance: {
              name: 'Fixer Tax Compliance',
              description: 'SARS registration, VAT, income tax, and fixer-specific deductions',
              cost_range: 'R600 - R1,800',
              processing_time: '5-10 business days'
            },
            insurance_setup: {
              name: 'Professional Insurance',
              description: 'Public liability, professional indemnity, and tools insurance',
              cost_range: 'R500 - R1,500',
              processing_time: '3-7 business days'
            },
            skills_certification: {
              name: 'Skills Certification',
              description: 'Accredited training certificates and skills verification',
              cost_range: 'R800 - R3,000',
              processing_time: '20-45 business days'
            },
            contractor_compliance: {
              name: 'Contractor Compliance',
              description: 'CIDB registration, contractor certificates, safety compliance',
              cost_range: 'R1,000 - R4,000',
              processing_time: '15-25 business days'
            }
          };
        } else {
          // Default client categories
          return {
            company_registration: {
              name: 'Company Registration',
              description: 'Assistance with registering new companies (Pty Ltd, CC, etc.)',
              cost_range: 'R1,500 - R3,500',
              processing_time: '10-15 business days'
            },
            sars_registration: {
              name: 'SARS Registration & Tax Compliance', 
              description: 'VAT registration, PAYE, UIF, SDL registration and compliance',
              cost_range: 'R800 - R2,500',
              processing_time: '5-10 business days'
            },
            labour_compliance: {
              name: 'Labour Law Compliance',
              description: 'Employment contracts, labour law compliance, CCMA assistance',
              cost_range: 'R1,000 - R2,000',
              processing_time: '3-7 business days'
            },
            bbbee_certification: {
              name: 'B-BBEE Certification',
              description: 'B-BBEE certificate applications and compliance management',
              cost_range: 'R3,000 - R8,000',
              processing_time: '15-30 business days'
            },
            licensing_permits: {
              name: 'Licensing & Permits',
              description: 'Trading licenses, municipal permits, industry-specific licenses',
              cost_range: 'R500 - R3,000',
              processing_time: '10-20 business days'
            },
            financial_compliance: {
              name: 'Financial Compliance',
              description: 'Annual returns, financial statements, audit compliance',
              cost_range: 'R2,000 - R5,000',
              processing_time: '5-15 business days'
            }
          };
        }
      };
      
      setCategories(getRoleBasedCategories());
    }
  };

  const fetchUserRequests = async () => {
    try {
      const token = localStorage.getItem('fixmate_token');
      const apiUrl = process.env.REACT_APP_BACKEND_URL || '/api';
      
      const response = await fetch(`${apiUrl}/api/compliance/requests`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setUserRequests(data.data);
          console.log('✅ User compliance requests loaded:', data.data.length);
        }
      } else {
        console.warn('⚠️ Could not fetch user requests (may be first time user)');
        setUserRequests([]);
      }
    } catch (error) {
      console.error('❌ Error fetching user compliance requests:', error);
      setUserRequests([]);
    }
  };

  const handleSubmitRequest = async (e) => {
    e.preventDefault();
    if (!requestForm.category || !requestForm.description) {
      alert('Please fill in all required fields');
      return;
    }

    setSubmitting(true);
    try {
      const token = localStorage.getItem('fixmate_token');
      const apiUrl = process.env.REACT_APP_BACKEND_URL || '/api';
      
      const response = await fetch(`${apiUrl}/api/compliance/request`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestForm)
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          alert('✅ Compliance request submitted successfully!');
          setRequestForm({
            category: '',
            description: '',
            urgency_level: 'normal',
            contact_preference: 'whatsapp'
          });
          fetchUserRequests(); // Refresh user requests
          setActiveTab('requests'); // Switch to requests tab
        }
      } else {
        const errorData = await response.json();
        alert(`❌ Failed to submit request: ${errorData.message || 'Please try again'}`);
      }
    } catch (error) {
      console.error('❌ Error submitting compliance request:', error);
      alert('❌ Network error. Please check your connection and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const fetchChecklist = async (category) => {
    setLoading(true);
    try {
      const apiUrl = process.env.REACT_APP_BACKEND_URL || '/api';
      const response = await fetch(`${apiUrl}/api/compliance/checklist/${category}`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setChecklist(data.data);
          console.log('✅ Compliance checklist loaded for:', category);
        }
      } else {
        console.warn('⚠️ Could not fetch checklist for:', category);
        setChecklist(null);
      }
    } catch (error) {
      console.error('❌ Error fetching compliance checklist:', error);
      setChecklist(null);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'submitted': 'bg-blue-100 text-blue-800',
      'in_review': 'bg-yellow-100 text-yellow-800',
      'quote_sent': 'bg-purple-100 text-purple-800',
      'in_progress': 'bg-orange-100 text-orange-800',
      'completed': 'bg-green-100 text-green-800',
      'on_hold': 'bg-gray-100 text-gray-800',
      'cancelled': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const getUrgencyColor = (urgency) => {
    const colors = {
      'low': 'bg-green-50 border-green-200 text-green-800',
      'normal': 'bg-blue-50 border-blue-200 text-blue-800',
      'high': 'bg-orange-50 border-orange-200 text-orange-800',
      'urgent': 'bg-red-50 border-red-200 text-red-800'
    };
    return colors[urgency] || 'bg-gray-50 border-gray-200 text-gray-800';
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="bg-white/20 p-3 rounded-lg">
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm3 1h6v4H7V5zm8 8v2a1 1 0 01-1 1H6a1 1 0 01-1-1v-2h10z" clipRule="evenodd" />
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold">
                {user?.role_info?.role === 'fixer' 
                  ? 'Professional Fixer Services' 
                  : 'Business Compliance Assistant'}
              </h1>
              <p className="opacity-90">
                {user?.role_info?.role === 'fixer' 
                  ? 'Professional licensing, business setup, and compliance for fixers'
                  : 'Company registrations, SARS, and business compliance support'}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm opacity-90">Welcome,</p>
            <p className="font-bold">{user?.first_name} {user?.last_name}</p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white rounded-lg shadow-sm">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6">
            {[
              { id: 'categories', label: 'Services', icon: '📋' },
              { id: 'request', label: 'New Request', icon: '➕' },
              { id: 'requests', label: 'My Requests', icon: '📄' },
              { id: 'checklist', label: 'Checklists', icon: '✅' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Services Overview Tab */}
          {activeTab === 'categories' && (
            <div className="space-y-6">
              <div className="text-center mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Professional Business Compliance Services
                </h2>
                <p className="text-gray-600">
                  Get expert assistance with all your business compliance needs in South Africa
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Object.entries(categories).map(([key, category]) => (
                  <div key={key} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {category.name}
                      </h3>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => {
                            setSelectedCategory(key);
                            fetchChecklist(key);
                            setActiveTab('checklist');
                          }}
                          className="text-indigo-600 hover:text-indigo-700 text-sm font-medium"
                        >
                          View Checklist
                        </button>
                      </div>
                    </div>
                    
                    <p className="text-gray-600 text-sm mb-4">
                      {category.description}
                    </p>
                    
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-500">Processing Time:</span>
                        <span className="font-medium">{category.processing_time}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-500">Cost Range:</span>
                        <span className="font-medium text-green-600">{category.cost_range}</span>
                      </div>
                    </div>
                    
                    <button
                      onClick={() => {
                        setRequestForm({...requestForm, category: key});
                        setActiveTab('request');
                      }}
                      className="w-full mt-4 bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
                    >
                      Request Service
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* New Request Tab */}
          {activeTab === 'request' && (
            <div className="max-w-2xl mx-auto space-y-6">
              <div className="text-center mb-8">
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  Submit Compliance Request
                </h2>
                <p className="text-gray-600">
                  Fill out the form below and our experts will contact you within 24 hours
                </p>
              </div>

              <form onSubmit={handleSubmitRequest} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Service Category *
                  </label>
                  <select
                    value={requestForm.category}
                    onChange={(e) => setRequestForm({...requestForm, category: e.target.value})}
                    className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  >
                    <option value="">Select a service category</option>
                    {Object.entries(categories).map(([key, category]) => (
                      <option key={key} value={key}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description *
                  </label>
                  <textarea
                    value={requestForm.description}
                    onChange={(e) => setRequestForm({...requestForm, description: e.target.value})}
                    rows={4}
                    placeholder="Please provide detailed information about your compliance needs..."
                    className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Urgency Level
                    </label>
                    <select
                      value={requestForm.urgency_level}
                      onChange={(e) => setRequestForm({...requestForm, urgency_level: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="low">Low - Can wait 2+ weeks</option>
                      <option value="normal">Normal - Within 1-2 weeks</option>
                      <option value="high">High - Within 1 week</option>
                      <option value="urgent">Urgent - ASAP</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Contact Preference
                    </label>
                    <select
                      value={requestForm.contact_preference}
                      onChange={(e) => setRequestForm({...requestForm, contact_preference: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="whatsapp">WhatsApp</option>
                      <option value="sms">SMS</option>
                      <option value="phone">Phone Call</option>
                      <option value="email">Email</option>
                    </select>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="flex">
                    <div className="flex-shrink-0">
                      <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div className="ml-3">
                      <h3 className="text-sm font-medium text-blue-800">What happens next?</h3>
                      <div className="mt-2 text-sm text-blue-700">
                        <ul className="list-disc pl-5 space-y-1">
                          <li>Our compliance expert will review your request</li>
                          <li>You'll receive a detailed quote within 24 hours</li>
                          <li>We'll provide a complete checklist of required documents</li>
                          <li>Work begins once you approve the quote</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={submitting}
                  className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? 'Submitting Request...' : 'Submit Compliance Request'}
                </button>
              </form>
            </div>
          )}

          {/* My Requests Tab */}
          {activeTab === 'requests' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">
                  Your Compliance Requests
                </h2>
                <button
                  onClick={() => setActiveTab('request')}
                  className="bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
                >
                  New Request
                </button>
              </div>

              {userRequests.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-gray-400 mb-4">
                    <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No requests yet</h3>
                  <p className="text-gray-600 mb-4">
                    You haven't submitted any compliance requests yet.
                  </p>
                  <button
                    onClick={() => setActiveTab('request')}
                    className="bg-indigo-600 text-white py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
                  >
                    Submit Your First Request
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  {userRequests.map((request) => (
                    <div key={request.id} className="bg-white border border-gray-200 rounded-lg p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="text-lg font-semibold text-gray-900">
                            {request.category_name}
                          </h3>
                          <p className="text-sm text-gray-500">
                            Request ID: {request.id.slice(0, 8)}...
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getUrgencyColor(request.urgency_level)}`}>
                            {request.urgency_level.toUpperCase()}
                          </span>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(request.status)}`}>
                            {request.status.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                      </div>
                      
                      <p className="text-gray-700 mb-4">{request.description}</p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Submitted:</span> 
                          <div className="font-medium">
                            {new Date(request.created_at).toLocaleDateString()}
                          </div>
                        </div>
                        {request.estimated_cost && (
                          <div>
                            <span className="text-gray-500">Estimated Cost:</span>
                            <div className="font-medium text-green-600">
                              R{request.estimated_cost.toLocaleString()}
                            </div>
                          </div>
                        )}
                        {request.estimated_completion && (
                          <div>
                            <span className="text-gray-500">Expected Completion:</span>
                            <div className="font-medium">
                              {new Date(request.estimated_completion).toLocaleDateString()}
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {request.admin_notes && (
                        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm font-medium text-gray-700">Admin Notes:</span>
                          <p className="text-sm text-gray-600 mt-1">{request.admin_notes}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Checklist Tab */}
          {activeTab === 'checklist' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">
                  Compliance Checklists
                </h2>
                <select
                  value={selectedCategory}
                  onChange={(e) => {
                    setSelectedCategory(e.target.value);
                    if (e.target.value) {
                      fetchChecklist(e.target.value);
                    }
                  }}
                  className="border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">Select a category</option>
                  {Object.entries(categories).map(([key, category]) => (
                    <option key={key} value={key}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>

              {loading ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
                  <p className="text-gray-600 mt-4">Generating checklist...</p>
                </div>
              ) : checklist ? (
                <div className="bg-white border border-gray-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    {checklist.name} Checklist
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 text-sm">
                    <div className="bg-blue-50 p-3 rounded-lg">
                      <span className="text-blue-700 font-medium">Processing Time:</span>
                      <div className="text-blue-900">{checklist.processing_time}</div>
                    </div>
                    <div className="bg-green-50 p-3 rounded-lg">
                      <span className="text-green-700 font-medium">Cost Range:</span>
                      <div className="text-green-900">{checklist.cost_range}</div>
                    </div>
                    <div className="bg-purple-50 p-3 rounded-lg">
                      <span className="text-purple-700 font-medium">Documents Needed:</span>
                      <div className="text-purple-900">{checklist.typical_docs?.length || 0} items</div>
                    </div>
                  </div>

                  {checklist.typical_docs && (
                    <div className="mb-6">
                      <h4 className="font-medium text-gray-900 mb-3">Required Documents:</h4>
                      <ul className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {checklist.typical_docs.map((doc, index) => (
                          <li key={index} className="flex items-center text-sm text-gray-700">
                            <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                            </svg>
                            {doc}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {checklist.checklist && (
                    <div className="prose max-w-none">
                      <div className="bg-gray-50 p-4 rounded-lg whitespace-pre-wrap">
                        {checklist.checklist}
                      </div>
                    </div>
                  )}

                  <div className="mt-6 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => {
                        setRequestForm({...requestForm, category: selectedCategory});
                        setActiveTab('request');
                      }}
                      className="bg-indigo-600 text-white py-2 px-6 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
                    >
                      Request This Service
                    </button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-gray-400 mb-4">
                    <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Select a category</h3>
                  <p className="text-gray-600">
                    Choose a compliance category above to view the detailed checklist
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default BusinessCompliance;