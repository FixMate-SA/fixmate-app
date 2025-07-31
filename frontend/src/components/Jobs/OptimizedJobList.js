import React, { memo, useMemo, useCallback } from 'react';
import { useInView } from 'react-intersection-observer';
import { useJobs } from '../../services/optimized_api';
import LoadingSpinner from '../Common/LoadingSpinner';

// Memoized Job Card Component
const JobCard = memo(({ job, onJobClick, userRole }) => {
  const handleClick = useCallback(() => {
    onJobClick(job.id);
  }, [job.id, onJobClick]);

  const statusColor = useMemo(() => {
    const colors = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'assigned': 'bg-blue-100 text-blue-800',
      'in_progress': 'bg-purple-100 text-purple-800',
      'completed': 'bg-green-100 text-green-800',
      'cancelled': 'bg-red-100 text-red-800'
    };
    return colors[job.status] || 'bg-gray-100 text-gray-800';
  }, [job.status]);

  const formattedDate = useMemo(() => {
    return new Date(job.created_at).toLocaleDateString();
  }, [job.created_at]);

  const truncatedDescription = useMemo(() => {
    return job.description?.length > 100 
      ? job.description.substring(0, 100) + '...'
      : job.description;
  }, [job.description]);

  return (
    <div 
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
      onClick={handleClick}
    >
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-800 capitalize">
          {job.service}
        </h3>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor}`}>
          {job.status?.replace('_', ' ')}
        </span>
      </div>
      
      <p className="text-gray-600 mb-3 text-sm">
        {truncatedDescription}
      </p>
      
      <div className="flex justify-between items-center text-sm text-gray-500">
        <span>📍 {job.location}</span>
        <span>{formattedDate}</span>
      </div>
      
      {job.estimated_price && (
        <div className="mt-3 text-right">
          <span className="text-lg font-semibold text-green-600">
            R{job.estimated_price}
          </span>
        </div>
      )}
      
      {userRole === 'fixer' && job.fixer_match_score && (
        <div className="mt-3 bg-blue-50 p-2 rounded">
          <div className="text-xs text-blue-600 font-medium">
            Match Score: {Math.round(job.fixer_match_score)}%
          </div>
        </div>
      )}
    </div>
  );
});

JobCard.displayName = 'JobCard';

// Memoized Job Filters Component
const JobFilters = memo(({ filters, onFiltersChange, loading }) => {
  const handleServiceChange = useCallback((e) => {
    onFiltersChange({ ...filters, service: e.target.value });
  }, [filters, onFiltersChange]);

  const handleStatusChange = useCallback((e) => {
    onFiltersChange({ ...filters, status: e.target.value });
  }, [filters, onFiltersChange]);

  const handleLocationChange = useCallback((e) => {
    onFiltersChange({ ...filters, location: e.target.value });
  }, [filters, onFiltersChange]);

  const handleClearFilters = useCallback(() => {
    onFiltersChange({});
  }, [onFiltersChange]);

  const hasActiveFilters = useMemo(() => {
    return Object.keys(filters).some(key => filters[key]);
  }, [filters]);

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-6">
      <div className="flex flex-wrap gap-4 items-center">
        <div className="flex-1 min-w-48">
          <select
            value={filters.service || ''}
            onChange={handleServiceChange}
            disabled={loading}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          >
            <option value="">All Services</option>
            <option value="plumbing">Plumbing</option>
            <option value="electrical">Electrical</option>
            <option value="carpentry">Carpentry</option>
            <option value="painting">Painting</option>
            <option value="cleaning">Cleaning</option>
            <option value="gardening">Gardening</option>
          </select>
        </div>
        
        <div className="flex-1 min-w-48">
          <select
            value={filters.status || ''}
            onChange={handleStatusChange}
            disabled={loading}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="assigned">Assigned</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        
        <div className="flex-1 min-w-48">
          <input
            type="text"
            placeholder="Filter by location..."
            value={filters.location || ''}
            onChange={handleLocationChange}
            disabled={loading}
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          />
        </div>
        
        {hasActiveFilters && (
          <button
            onClick={handleClearFilters}
            disabled={loading}
            className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50"
          >
            Clear Filters
          </button>
        )}
      </div>
    </div>
  );
});

JobFilters.displayName = 'JobFilters';

// Memoized Empty State Component
const EmptyJobsState = memo(({ filters, onCreateJob }) => {
  const hasFilters = useMemo(() => {
    return Object.keys(filters).some(key => filters[key]);
  }, [filters]);

  return (
    <div className="text-center py-12">
      <div className="text-6xl mb-4">📋</div>
      <h3 className="text-xl font-semibold text-gray-800 mb-2">
        {hasFilters ? 'No jobs match your filters' : 'No jobs available'}
      </h3>
      <p className="text-gray-600 mb-6 max-w-md mx-auto">
        {hasFilters 
          ? 'Try adjusting your filters to see more results.'
          : 'Get started by creating your first service request.'
        }
      </p>
      {!hasFilters && onCreateJob && (
        <button
          onClick={onCreateJob}
          className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors"
        >
          Create Your First Job
        </button>
      )}
    </div>
  );
});

EmptyJobsState.displayName = 'EmptyJobsState';

// Main Optimized Job List Component
const OptimizedJobList = ({ userRole = 'client', showCreateButton = true }) => {
  const [filters, setFilters] = React.useState({});
  const [selectedJob, setSelectedJob] = React.useState(null);

  // Optimized query with proper dependencies
  const { 
    data: jobsData, 
    isLoading, 
    error, 
    refetch 
  } = useJobs(filters, {
    keepPreviousData: true, // Maintain previous data while fetching new
    refetchOnWindowFocus: false,
    staleTime: 1000 * 60 * 2, // 2 minutes
  });

  // Intersection observer for pagination trigger
  const { ref: loadMoreRef, inView } = useInView({
    threshold: 0,
    rootMargin: '100px 0px', // Load more when 100px from bottom
  });

  // Memoized job list
  const jobs = useMemo(() => {
    return jobsData?.jobs || [];
  }, [jobsData?.jobs]);

  // Callback handlers with useCallback for performance
  const handleFiltersChange = useCallback((newFilters) => {
    setFilters(newFilters);
  }, []);

  const handleJobClick = useCallback((jobId) => {
    setSelectedJob(jobId);
    // Navigate to job details or open modal
    window.location.href = `/jobs/${jobId}`;
  }, []);

  const handleCreateJob = useCallback(() => {
    window.location.href = '/jobs/create';
  }, []);

  const handleRetry = useCallback(() => {
    refetch();
  }, [refetch]);

  // Error state
  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-6xl mb-4">😵</div>
        <h3 className="text-xl font-semibold text-gray-800 mb-2">
          Oops! Something went wrong
        </h3>
        <p className="text-gray-600 mb-6">
          We couldn't load the jobs. Please try again.
        </p>
        <button
          onClick={handleRetry}
          className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Create Button */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {userRole === 'fixer' ? 'Available Jobs' : 'My Jobs'}
          </h1>
          <p className="text-gray-600 mt-1">
            {isLoading ? 'Loading jobs...' : `${jobs.length} job${jobs.length !== 1 ? 's' : ''} found`}
          </p>
        </div>
        
        {showCreateButton && userRole === 'client' && (
          <button
            onClick={handleCreateJob}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors flex items-center"
          >
            <span className="mr-2">+</span>
            Create Job
          </button>
        )}
      </div>

      {/* Filters */}
      <JobFilters 
        filters={filters}
        onFiltersChange={handleFiltersChange}
        loading={isLoading}
      />

      {/* Loading State */}
      {isLoading && jobs.length === 0 && (
        <div className="flex justify-center py-12">
          <LoadingSpinner message="Loading jobs..." size="large" />
        </div>
      )}

      {/* Jobs Grid */}
      {jobs.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {jobs.map((job) => (
            <JobCard
              key={job.id}
              job={job}
              onJobClick={handleJobClick}
              userRole={userRole}
            />
          ))}
        </div>
      ) : !isLoading && (
        <EmptyJobsState 
          filters={filters}
          onCreateJob={showCreateButton ? handleCreateJob : undefined}
        />
      )}

      {/* Load More Trigger */}
      {jobs.length > 0 && (
        <div ref={loadMoreRef} className="h-10 flex items-center justify-center">
          {inView && isLoading && (
            <LoadingSpinner message="Loading more jobs..." size="small" />
          )}
        </div>
      )}
    </div>
  );
};

export default memo(OptimizedJobList);