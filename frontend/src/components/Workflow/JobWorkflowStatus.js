import React, { useState, useEffect, useCallback } from 'react';
import { useLanguage } from '../../contexts/LanguageContext';

const JobWorkflowStatus = ({ jobId, initialStatus }) => {
  const { t } = useLanguage();
  const [status, setStatus] = useState(initialStatus || {});
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const fetchStatus = useCallback(async () => {
    if (!jobId) return;

    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/jobs/${jobId}/workflow-status`);
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
        setLastUpdated(new Date());
      }
    } catch (error) {
      console.error('Error fetching workflow status:', error);
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    if (jobId && !initialStatus) {
      fetchStatus();
    }

    // Set up polling for real-time updates
    const interval = setInterval(fetchStatus, 10000); // Poll every 10 seconds

    return () => clearInterval(interval);
  }, [jobId, fetchStatus, initialStatus]);

  const getStatusIcon = (stage) => {
    switch (stage) {
      case 'terms_accepted':
      case 'eligible_check':
        return '✅';
      case 'notifying':
        return '📢';
      case 'waiting_assignment':
        return '⏳';
      case 'assigned':
        return '👤';
      case 'tracking':
        return '🗺️';
      case 'completed':
        return '🎉';
      case 'emergency':
        return '🚨';
      case 'cancelled':
        return '❌';
      default:
        return '⏳';
    }
  };

  const getStatusColor = (stage) => {
    switch (stage) {
      case 'terms_accepted':
      case 'eligible_check':
      case 'completed':
        return 'text-green-600 bg-green-50';
      case 'notifying':
      case 'waiting_assignment':
        return 'text-blue-600 bg-blue-50';
      case 'assigned':
      case 'tracking':
        return 'text-purple-600 bg-purple-50';
      case 'emergency':
        return 'text-red-600 bg-red-50';
      case 'cancelled':
        return 'text-gray-600 bg-gray-50';
      default:
        return 'text-yellow-600 bg-yellow-50';
    }
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return null;
    try {
      const date = new Date(dateString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return null;
    }
  };

  const renderTimelineItem = (icon, title, description, isActive = false, timestamp = null) => (
    <div className={`flex items-start space-x-3 ${isActive ? 'opacity-100' : 'opacity-60'}`}>
      <div className={`flex items-center justify-center w-8 h-8 rounded-full ${
        isActive ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
      }`}>
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <p className={`text-sm font-medium ${isActive ? 'text-gray-900' : 'text-gray-500'}`}>
          {title}
        </p>
        <p className={`text-sm ${isActive ? 'text-gray-700' : 'text-gray-400'}`}>
          {description}
        </p>
        {timestamp && (
          <p className="text-xs text-gray-400 mt-1">
            {timestamp}
          </p>
        )}
      </div>
    </div>
  );

  const getCurrentStageText = () => {
    switch (status.workflow_stage) {
      case 'terms_accepted':
        return t('termsAcceptedStage', 'Terms accepted, checking eligibility');
      case 'eligible_check':
        return t('eligibleCheckStage', 'Finding eligible fixers');
      case 'notifying':
        return t('notifyingStage', 'Notifying fixers');
      case 'waiting_assignment':
        return t('waitingAssignmentStage', 'Waiting for fixer acceptance');
      case 'assigned':
        return t('assignedStage', 'Fixer assigned, preparing for work');
      case 'tracking':
        return t('trackingStage', 'Fixer en route - live tracking active');
      case 'completed':
        return t('completedStage', 'Job completed successfully');
      case 'emergency':
        return t('emergencyStage', 'Emergency escalation - urgent attention');
      case 'cancelled':
        return t('cancelledStage', 'Job cancelled');
      default:
        return t('unknownStage', 'Processing...');
    }
  };

  if (!status.job_id) {
    return (
      <div className="bg-gray-50 rounded-lg p-4">
        <p className="text-gray-500 text-center">No workflow status available</p>
      </div>
    );
  }

  return (
    <div className="bg-white border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          🔄 {t('workflowStatus', 'Workflow Status')}
        </h3>
        <button
          onClick={fetchStatus}
          disabled={loading}
          className="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
        >
          {loading ? '↻' : '🔄'} {t('refresh', 'Refresh')}
        </button>
      </div>

      {/* Current Status Banner */}
      <div className={`rounded-lg p-4 mb-6 ${getStatusColor(status.workflow_stage)}`}>
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getStatusIcon(status.workflow_stage)}</span>
          <div>
            <h4 className="font-medium">
              {status.workflow_stage?.replace('_', ' ').toUpperCase()}
            </h4>
            <p className="text-sm">{getCurrentStageText()}</p>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-lg font-bold text-gray-900">
            {status.eligible_fixers_count || 0}
          </div>
          <div className="text-xs text-gray-500">
            {t('eligibleFixers', 'Eligible Fixers')}
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-lg font-bold text-gray-900">
            {status.notified_fixers_count || 0}
          </div>
          <div className="text-xs text-gray-500">
            {t('notifiedFixers', 'Notified Fixers')}
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className="text-lg font-bold text-gray-900">
            {status.assignment_attempts || 0}
          </div>
          <div className="text-xs text-gray-500">
            {t('attempts', 'Attempts')}
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <div className={`text-lg font-bold ${status.priority_level === 'emergency' ? 'text-red-600' : 'text-gray-900'}`}>
            {status.priority_level?.toUpperCase() || 'NORMAL'}
          </div>
          <div className="text-xs text-gray-500">
            {t('priority', 'Priority')}
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-gray-900 mb-3">
          {t('progressTimeline', 'Progress Timeline')}
        </h4>

        <div className="space-y-4">
          {renderTimelineItem(
            '⚖️',
            t('termsAccepted', 'Terms Accepted'),
            t('clientAcceptedTerms', 'Client accepted platform terms'),
            status.terms_accepted,
            null
          )}

          {renderTimelineItem(
            '🔍',
            t('findingFixers', 'Finding Fixers'),
            `${status.eligible_fixers_count || 0} ${t('eligibleFixersFound', 'eligible fixers found')}`,
            status.eligible_fixers_count > 0,
            null
          )}

          {renderTimelineItem(
            '📢',
            t('notifyingFixers', 'Notifying Fixers'),
            `${status.notified_fixers_count || 0} ${t('fixersNotified', 'fixers notified via app and WhatsApp')}`,
            status.workflow_stage === 'notifying' || status.notified_fixers_count > 0,
            null
          )}

          {renderTimelineItem(
            status.fixer_assigned ? '✅' : '⏳',
            t('fixerAssignment', 'Fixer Assignment'),
            status.fixer_assigned 
              ? t('fixerAssigned', 'Fixer assigned and preparing')
              : t('waitingForAcceptance', 'Waiting for fixer acceptance'),
            status.workflow_stage === 'waiting_assignment' || status.fixer_assigned,
            status.assignment_timeout ? formatDateTime(status.assignment_timeout) : null
          )}

          {status.tracking_active && renderTimelineItem(
            '🗺️',
            t('liveTracking', 'Live Tracking'),
            t('trackingActive', 'Live location tracking active'),
            true,
            null
          )}

          {status.estimated_arrival && renderTimelineItem(
            '🕐',
            t('estimatedArrival', 'Estimated Arrival'),
            formatDateTime(status.estimated_arrival),
            true,
            null
          )}
        </div>
      </div>

      {/* Special Alerts */}
      {status.is_emergency_escalated && (
        <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <span className="text-red-600 text-lg">🚨</span>
            <div>
              <h4 className="text-red-800 font-medium">
                {t('emergencyEscalation', 'Emergency Escalation')}
              </h4>
              <p className="text-red-700 text-sm">
                {t('emergencyMessage', 'This job has been escalated due to timeout. All available fixers have been notified with urgent priority.')}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Auto-refresh indicator */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          {t('lastUpdated', 'Last updated')}: {lastUpdated.toLocaleTimeString()} • 
          {t('autoRefresh', 'Auto-refreshes every 10 seconds')}
        </p>
      </div>
    </div>
  );
};

export default JobWorkflowStatus;