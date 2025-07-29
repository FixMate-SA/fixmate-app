import React, { useState, useEffect } from 'react';
import { apiService } from '../../services/api';
import { Link } from 'react-router-dom';

const FixerList = () => {
  const [fixers, setFixers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedService, setSelectedService] = useState('');

  const serviceOptions = [
    'Plumbing',
    'Electrical',
    'Carpentry',
    'Painting',
    'Cleaning',
    'Gardening',
    'Handyman',
    'Appliance Repair',
    'Roofing',
    'Flooring',
    'HVAC',
  ];

  useEffect(() => {
    const fetchFixers = async () => {
      try {
        const response = await apiService.getFixers();
        setFixers(response.data);
      } catch (err) {
        console.error('Error fetching fixers:', err);
        setError('Failed to load fixers');
      } finally {
        setLoading(false);
      }
    };

    fetchFixers();
  }, []);

  const parseServices = (services) => {
    try {
      // If it's already an array, return it
      if (Array.isArray(services)) return services;
      
      // If it's a JSON string, parse it
      if (typeof services === 'string' && services.startsWith('[')) {
        return JSON.parse(services);
      }
      
      // If it's comma-separated, split it
      if (typeof services === 'string' && services.includes(',')) {
        return services.split(',').map(s => s.trim());
      }
      
      // Single service as string
      if (typeof services === 'string') {
        return [services];
      }
      
      return [];
    } catch (error) {
      console.error('Error parsing services:', services, error);
      return [];
    }
  };

  const filteredFixers = fixers.filter(fixer => {
    const matchesSearch = fixer.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         fixer.location.toLowerCase().includes(searchTerm.toLowerCase());
    
    const servicesArray = parseServices(fixer.services);
    const matchesService = !selectedService || 
                          servicesArray.some(service => 
                            service.toLowerCase().includes(selectedService.toLowerCase())
                          );
    
    return matchesSearch && matchesService;
  });

  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push(<span key={i} className="text-yellow-400">★</span>);
    }

    if (hasHalfStar) {
      stars.push(<span key="half" className="text-yellow-400">☆</span>);
    }

    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(<span key={`empty-${i}`} className="text-gray-300">★</span>);
    }

    return stars;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Find Fixers</h1>
        <div className="text-sm text-gray-500">
          {filteredFixers.length} fixers available
        </div>
      </div>

      {/* Search and Filter */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="search" className="block text-sm font-medium text-gray-700 mb-2">
              Search by name or location
            </label>
            <input
              type="text"
              id="search"
              placeholder="Search fixers..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label htmlFor="service" className="block text-sm font-medium text-gray-700 mb-2">
              Filter by service
            </label>
            <select
              id="service"
              value={selectedService}
              onChange={(e) => setSelectedService(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All services</option>
              {serviceOptions.map((service) => (
                <option key={service} value={service}>
                  {service}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Fixers Grid */}
      {filteredFixers.length === 0 ? (
        <div className="text-center py-12">
          <span className="text-6xl">🔧</span>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No fixers found</h3>
          <p className="mt-2 text-gray-500">
            Try adjusting your search or filter criteria.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredFixers.map((fixer) => (
            <div key={fixer.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-bold text-lg">
                      {fixer.name.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{fixer.name}</h3>
                    <div className="flex items-center space-x-1">
                      {renderStars(fixer.rating)}
                      <span className="text-sm text-gray-600 ml-2">
                        ({fixer.rating.toFixed(1)})
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-gray-500">{fixer.total_jobs} jobs</div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <span>📍</span>
                  <span>{fixer.location}</span>
                </div>

                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <span>📧</span>
                  <span>{fixer.email || 'Not provided'}</span>
                </div>

                <div className="flex items-center space-x-2 text-sm text-gray-600">
                  <span>📱</span>
                  <span>{fixer.phone}</span>
                </div>

                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Services:</p>
                  <div className="flex flex-wrap gap-2">
                    {parseServices(fixer.services).map((service, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                      >
                        {service}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <Link
                    to={`/fixers/${fixer.id}`}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    View Profile
                  </Link>
                  <button
                    onClick={() => {
                      // Create a job with this fixer's service
                      const services = parseServices(fixer.services);
                      const queryParams = new URLSearchParams({
                        service: services[0],
                        fixerId: fixer.id
                      });
                      window.location.href = `/jobs/create?${queryParams}`;
                    }}
                    className="px-3 py-1 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                  >
                    Hire Now
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FixerList;