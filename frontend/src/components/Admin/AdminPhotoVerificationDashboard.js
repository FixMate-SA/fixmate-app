import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const AdminPhotoVerificationDashboard = () => {
  const { user } = useAuth();
  const [pendingVerifications, setPendingVerifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [processingIds, setProcessingIds] = useState(new Set());
  const [selectedVerification, setSelectedVerification] = useState(null);
  const [showPhotoModal, setShowPhotoModal] = useState(false);
  const [verificationAction, setVerificationAction] = useState('');
  const [verificationComments, setVerificationComments] = useState('');

  useEffect(() => {
    if (user?.role === 'admin' || user?.role === 'super_admin') {
      fetchPendingVerifications();
    }
  }, [user]);

  const fetchPendingVerifications = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/photo-verifications/pending`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setPendingVerifications(data.pending_verifications || []);
      } else {
        setError('Failed to load pending verifications');
      }
    } catch (err) {
      console.error('Error fetching pending verifications:', err);
      setError('Error loading pending verifications');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyPhotos = async (verificationId, decision, comments = '') => {
    setProcessingIds(prev => new Set(prev).add(verificationId));
    
    try {
      const response = await fetch(
        `${import.meta.env.REACT_APP_BACKEND_URL}/api/admin/photo-verification/${verificationId}/verify`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            decision: decision,
            comments: comments
          })
        }
      );

      if (response.ok) {
        // Remove from pending list
        setPendingVerifications(prev => 
          prev.filter(v => v.verification_id !== verificationId)
        );
        
        // Close modal if open
        if (selectedVerification?.verification_id === verificationId) {
          setShowPhotoModal(false);
          setSelectedVerification(null);
        }
        
        // Show success message (you could add a toast notification here)
        console.log(`Photo verification ${decision} successfully`);
      } else {
        setError(`Failed to ${decision} photos`);
      }
    } catch (err) {
      console.error('Error verifying photos:', err);
      setError('Error processing verification');
    } finally {
      setProcessingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(verificationId);
        return newSet;
      });
    }
  };

  const openPhotoModal = (verification) => {
    setSelectedVerification(verification);
    setShowPhotoModal(true);
    setVerificationAction('');
    setVerificationComments('');
  };

  const submitVerification = () => {
    if (!verificationAction) {
      setError('Please select an action');
      return;
    }

    if (verificationAction === 'rejected' && !verificationComments.trim()) {
      setError('Comments are required when rejecting photos');
      return;
    }

    handleVerifyPhotos(selectedVerification.verification_id, verificationAction, verificationComments);
  };

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      needs_more: 'bg-blue-100 text-blue-800'
    };
    
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  const getQualityScore = (score) => {
    if (!score) return { color: 'text-gray-500', label: 'Not assessed' };
    
    if (score >= 80) return { color: 'text-green-600', label: 'Excellent' };
    if (score >= 60) return { color: 'text-blue-600', label: 'Good' };
    if (score >= 40) return { color: 'text-yellow-600', label: 'Fair' };
    return { color: 'text-red-600', label: 'Poor' };
  };

  const PhotoModal = () => {
    if (!selectedVerification || !showPhotoModal) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-lg shadow-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
          <div className="p-6">
            {/* Modal Header */}
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Photo Verification Review</h2>
                <p className="text-gray-600">Job: {selectedVerification.job_details?.service} - {selectedVerification.job_details?.location}</p>
              </div>
              <button
                onClick={() => setShowPhotoModal(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Job Details */}
            <div className="bg-gray-50 rounded-lg p-4 mb-6">
              <h3 className="font-medium text-gray-900 mb-2">Job Information</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="font-medium text-gray-700">Client:</span>
                  <div>{selectedVerification.job_details?.client_name}</div>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Fixer:</span>
                  <div>{selectedVerification.job_details?.fixer_name}</div>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Price:</span>
                  <div>R{selectedVerification.job_details?.final_price}</div>
                </div>
                <div>
                  <span className="font-medium text-gray-700">Required:</span>
                  <div>{selectedVerification.is_required ? 'Yes' : 'No'}</div>
                </div>
              </div>
              {selectedVerification.requirement_reason && (
                <div className="mt-2 text-sm">
                  <span className="font-medium text-gray-700">Reason:</span>
                  <span className="ml-2">{selectedVerification.requirement_reason}</span>
                </div>
              )}
            </div>

            {/* AI Analysis */}
            {selectedVerification.quality_assessment && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="font-medium text-blue-900 mb-2">🤖 AI Analysis</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-blue-800">Quality Score:</span>
                    <div className={getQualityScore(selectedVerification.quality_assessment.photo_quality_score).color}>
                      {selectedVerification.quality_assessment.photo_quality_score || 'N/A'}/100
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-blue-800">Before/After:</span>
                    <div>{selectedVerification.quality_assessment.has_clear_before_after ? '✅' : '❌'}</div>
                  </div>
                  <div>
                    <span className="font-medium text-blue-800">Work Shown:</span>
                    <div>{selectedVerification.quality_assessment.shows_completed_work ? '✅' : '❌'}</div>
                  </div>
                  <div>
                    <span className="font-medium text-blue-800">AI Confidence:</span>
                    <div>{selectedVerification.quality_assessment.ai_confidence || 'N/A'}%</div>
                  </div>
                </div>
                
                {selectedVerification.flagged_issues && selectedVerification.flagged_issues.length > 0 && (
                  <div className="mt-3">
                    <span className="font-medium text-blue-800">Flagged Issues:</span>
                    <ul className="mt-1 list-disc list-inside text-blue-700 text-sm">
                      {selectedVerification.flagged_issues.map((issue, index) => (
                        <li key={index}>{issue}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}

            {/* Photo Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              {/* Before Photos */}
              {selectedVerification.photo_counts.before > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-3">📷 Before Photos ({selectedVerification.photo_counts.before})</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {Array.from({ length: selectedVerification.photo_counts.before }).map((_, index) => (
                      <div key={index} className="bg-gray-200 rounded-lg aspect-square flex items-center justify-center">
                        <span className="text-gray-500">Before Photo {index + 1}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* After Photos */}
              {selectedVerification.photo_counts.after > 0 && (
                <div>
                  <h3 className="font-medium text-gray-900 mb-3">✅ After Photos ({selectedVerification.photo_counts.after})</h3>
                  <div className="grid grid-cols-2 gap-2">
                    {Array.from({ length: selectedVerification.photo_counts.after }).map((_, index) => (
                      <div key={index} className="bg-gray-200 rounded-lg aspect-square flex items-center justify-center">
                        <span className="text-gray-500">After Photo {index + 1}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Progress Photos */}
            {selectedVerification.photo_counts.progress > 0 && (
              <div className="mb-6">
                <h3 className="font-medium text-gray-900 mb-3">🔄 Progress Photos ({selectedVerification.photo_counts.progress})</h3>
                <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
                  {Array.from({ length: selectedVerification.photo_counts.progress }).map((_, index) => (
                    <div key={index} className="bg-gray-200 rounded-lg aspect-square flex items-center justify-center">
                      <span className="text-gray-500 text-sm">Progress {index + 1}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Verification Actions */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-medium text-gray-900 mb-4">Verification Decision</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <label className={`cursor-pointer rounded-lg border p-3 transition-colors ${verificationAction === 'approved' ? 'border-green-500 bg-green-50' : 'border-gray-300 bg-white hover:border-green-400'}`}>
                  <input
                    type="radio"
                    name="verificationAction"
                    value="approved"
                    checked={verificationAction === 'approved'}
                    onChange={(e) => setVerificationAction(e.target.value)}
                    className="sr-only"
                  />
                  <div className="text-center">
                    <div className="text-xl mb-1">✅</div>
                    <div className="font-medium text-green-900">Approve</div>
                    <div className="text-sm text-green-700">Photos are satisfactory</div>
                  </div>
                </label>

                <label className={`cursor-pointer rounded-lg border p-3 transition-colors ${verificationAction === 'needs_more' ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white hover:border-blue-400'}`}>
                  <input
                    type="radio"
                    name="verificationAction"
                    value="needs_more"
                    checked={verificationAction === 'needs_more'}
                    onChange={(e) => setVerificationAction(e.target.value)}
                    className="sr-only"
                  />
                  <div className="text-center">
                    <div className="text-xl mb-1">📸</div>
                    <div className="font-medium text-blue-900">Need More</div>
                    <div className="text-sm text-blue-700">Request additional photos</div>
                  </div>
                </label>

                <label className={`cursor-pointer rounded-lg border p-3 transition-colors ${verificationAction === 'rejected' ? 'border-red-500 bg-red-50' : 'border-gray-300 bg-white hover:border-red-400'}`}>
                  <input
                    type="radio"
                    name="verificationAction"
                    value="rejected"
                    checked={verificationAction === 'rejected'}
                    onChange={(e) => setVerificationAction(e.target.value)}
                    className="sr-only"
                  />
                  <div className="text-center">
                    <div className="text-xl mb-1">❌</div>
                    <div className="font-medium text-red-900">Reject</div>
                    <div className="text-sm text-red-700">Photos are inadequate</div>
                  </div>
                </label>
              </div>

              <div className="mb-4">
                <label htmlFor="verificationComments" className="block text-sm font-medium text-gray-700 mb-2">
                  Comments {verificationAction === 'rejected' && <span className="text-red-500">*</span>}
                </label>
                <textarea
                  id="verificationComments"
                  value={verificationComments}
                  onChange={(e) => setVerificationComments(e.target.value)}
                  rows={3}
                  placeholder="Provide feedback or reasons for your decision..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex items-center justify-end space-x-3">
                <button
                  onClick={() => setShowPhotoModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={submitVerification}
                  disabled={!verificationAction || processingIds.has(selectedVerification.verification_id)}
                  className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {processingIds.has(selectedVerification.verification_id) ? 'Processing...' : 'Submit Decision'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (user?.role !== 'admin' && user?.role !== 'super_admin') {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
          Access denied. Admin privileges required.
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">📸 Photo Verification Dashboard</h1>
        <p className="text-gray-600">Review and verify job completion photos submitted by fixers</p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
          {error}
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading pending verifications...</p>
          </div>
        </div>
      ) : (
        <>
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Pending Reviews</p>
                  <p className="text-2xl font-bold text-blue-600">{pendingVerifications.length}</p>
                </div>
                <div className="text-3xl">📋</div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">High Priority</p>
                  <p className="text-2xl font-bold text-red-600">
                    {pendingVerifications.filter(v => v.job_details?.final_price >= 1000).length}
                  </p>
                </div>
                <div className="text-3xl">⚡</div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">AI Flagged</p>
                  <p className="text-2xl font-bold text-yellow-600">
                    {pendingVerifications.filter(v => v.flagged_issues && v.flagged_issues.length > 0).length}
                  </p>
                </div>
                <div className="text-3xl">🤖</div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">This Week</p>
                  <p className="text-2xl font-bold text-green-600">
                    {pendingVerifications.filter(v => {
                      const weekAgo = new Date();
                      weekAgo.setDate(weekAgo.getDate() - 7);
                      return new Date(v.created_at) >= weekAgo;
                    }).length}
                  </p>
                </div>
                <div className="text-3xl">📅</div>
              </div>
            </div>
          </div>

          {/* Pending Verifications List */}
          {pendingVerifications.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 text-6xl mb-4">📸</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">No Pending Photo Verifications</h3>
              <p className="text-gray-600">All submitted photos have been reviewed!</p>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Pending Photo Verifications</h2>
              </div>
              
              <div className="divide-y divide-gray-200">
                {pendingVerifications.map((verification) => (
                  <div key={verification.verification_id} className="p-6 hover:bg-gray-50 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h3 className="text-lg font-medium text-gray-900">
                            {verification.job_details?.service} - {verification.job_details?.location}
                          </h3>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(verification.status)}`}>
                            {verification.status}
                          </span>
                          {verification.is_required && (
                            <span className="bg-red-100 text-red-800 text-xs font-medium px-2 py-1 rounded-full">
                              Required
                            </span>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-3">
                          <div>
                            <span className="font-medium">Client:</span> {verification.job_details?.client_name}
                          </div>
                          <div>
                            <span className="font-medium">Fixer:</span> {verification.job_details?.fixer_name}
                          </div>
                          <div>
                            <span className="font-medium">Price:</span> R{verification.job_details?.final_price}
                          </div>
                          <div>
                            <span className="font-medium">Photos:</span> 
                            <span className="ml-1">
                              {verification.photo_counts.before}📷 {verification.photo_counts.after}✅ {verification.photo_counts.progress}🔄
                            </span>
                          </div>
                        </div>

                        {verification.quality_assessment && (
                          <div className="flex items-center space-x-4 text-sm">
                            <div className={`${getQualityScore(verification.quality_assessment.photo_quality_score).color}`}>
                              Quality: {verification.quality_assessment.photo_quality_score || 'N/A'}/100
                            </div>
                            <div>
                              AI Confidence: {verification.quality_assessment.ai_confidence || 'N/A'}%
                            </div>
                            {verification.flagged_issues && verification.flagged_issues.length > 0 && (
                              <div className="text-yellow-600">
                                ⚠️ {verification.flagged_issues.length} issues flagged
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      <div className="flex items-center space-x-3">
                        <button
                          onClick={() => openPhotoModal(verification)}
                          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                        >
                          Review Photos
                        </button>
                        
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleVerifyPhotos(verification.verification_id, 'approved')}
                            disabled={processingIds.has(verification.verification_id)}
                            className="px-3 py-1 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors text-sm"
                          >
                            ✅ Approve
                          </button>
                          <button
                            onClick={() => handleVerifyPhotos(verification.verification_id, 'rejected', 'Quick rejection')}
                            disabled={processingIds.has(verification.verification_id)}
                            className="px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50 transition-colors text-sm"
                          >
                            ❌ Reject
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {/* Photo Modal */}
      <PhotoModal />
    </div>
  );
};

export default AdminPhotoVerificationDashboard;