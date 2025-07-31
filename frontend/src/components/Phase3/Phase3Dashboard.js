import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useLanguage } from '../../contexts/LanguageContext';
import JobTrackingControls from '../Tracking/JobTrackingControls';
import JobTrackingStatus from '../Tracking/JobTrackingStatus';
import FixerReputationDashboard from '../Gamification/FixerReputationDashboard';
import AIChatAssistant, { AIChatButton } from '../AI/AIChatAssistant';

const Phase3Dashboard = () => {
  const { user } = useAuth();
  const { language, translations } = useLanguage();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedJobId, setSelectedJobId] = useState('');
  const [selectedFixerId, setSelectedFixerId] = useState('');
  const [showAIChat, setShowAIChat] = useState(false);

  // Sample data for demonstration - in real app, this would come from API
  const sampleJobs = [
    { id: 'job-123', title: 'Plumbing Repair', status: 'in_progress' },
    { id: 'job-124', title: 'Electrical Fix', status: 'assigned' },
    { id: 'job-125', title: 'Carpentry Work', status: 'tracking' }
  ];

  const sampleFixers = [
    { id: 'fixer-456', name: 'John Smith', service: 'Plumbing' },
    { id: 'fixer-457', name: 'Sarah Johnson', service: 'Electrical' },
    { id: 'fixer-458', name: 'Mike Brown', service: 'Carpentry' }
  ];

  const tabs = [
    { id: 'overview', label: translations.overview || 'Overview', icon: '📊' },
    { id: 'tracking', label: translations.job_tracking || 'Job Tracking', icon: '📍' },
    { id: 'reputation', label: translations.reputation || 'Reputation', icon: '🏆' },
    { id: 'analytics', label: translations.analytics || 'Analytics', icon: '📈' }
  ];

  const renderOverview = () => (
    <div className="space-y-6">
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-lg">
        <h2 className="text-2xl font-bold mb-2">
          {translations.phase3_welcome || 'Welcome to Phase 3: Automation & Engagement'}
        </h2>
        <p className="text-blue-100">
          {translations.phase3_description || 'Experience real-time tracking, gamification, and AI-powered assistance.'}
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center mb-4">
            <div className="text-3xl mr-3">📍</div>
            <div>
              <h3 className="font-semibold text-gray-800">
                {translations.real_time_tracking || 'Real-Time Tracking'}
              </h3>
              <p className="text-sm text-gray-600">
                {translations.tracking_description || 'Live location updates and ETA calculations'}
              </p>
            </div>
          </div>
          <button
            onClick={() => setActiveTab('tracking')}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition-colors"
          >
            {translations.start_tracking || 'Start Tracking'}
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center mb-4">
            <div className="text-3xl mr-3">🏆</div>
            <div>
              <h3 className="font-semibold text-gray-800">
                {translations.gamification || 'Gamification'}
              </h3>
              <p className="text-sm text-gray-600">
                {translations.gamification_description || 'Earn badges, climb tiers, build reputation'}
              </p>
            </div>
          </div>
          <button
            onClick={() => setActiveTab('reputation')}
            className="w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 transition-colors"
          >
            {translations.view_reputation || 'View Reputation'}
          </button>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center mb-4">
            <div className="text-3xl mr-3">🤖</div>
            <div>
              <h3 className="font-semibold text-gray-800">
                {translations.ai_assistant || 'AI Assistant'}
              </h3>
              <p className="text-sm text-gray-600">
                {translations.ai_description || 'Get instant help in multiple languages'}
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowAIChat(true)}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
          >
            {translations.chat_now || 'Chat Now'}
          </button>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          {translations.recent_activity || 'Recent Activity'}
        </h3>
        <div className="space-y-3">
          <div className="flex items-center p-3 bg-green-50 rounded-lg">
            <div className="text-green-600 mr-3">✅</div>
            <div className="flex-1">
              <div className="font-medium text-gray-800">Job Completed</div>
              <div className="text-sm text-gray-600">Plumbing repair at 123 Main St</div>
            </div>
            <div className="text-xs text-gray-500">2 hours ago</div>
          </div>
          <div className="flex items-center p-3 bg-blue-50 rounded-lg">
            <div className="text-blue-600 mr-3">🏆</div>
            <div className="flex-1">
              <div className="font-medium text-gray-800">Badge Earned</div>
              <div className="text-sm text-gray-600">Earned "Punctual Pro" badge</div>
            </div>
            <div className="text-xs text-gray-500">1 day ago</div>
          </div>
          <div className="flex items-center p-3 bg-purple-50 rounded-lg">
            <div className="text-purple-600 mr-3">⬆️</div>
            <div className="flex-1">
              <div className="font-medium text-gray-800">Tier Upgrade</div>
              <div className="text-sm text-gray-600">Promoted to Silver tier</div>
            </div>
            <div className="text-xs text-gray-500">3 days ago</div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTracking = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          {translations.job_selection || 'Select Job for Tracking'}
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {translations.select_job || 'Select Job:'}
            </label>
            <select
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">{translations.choose_job || 'Choose a job...'}</option>
              {sampleJobs.map(job => (
                <option key={job.id} value={job.id}>
                  {job.title} ({job.status})
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <h4 className="text-lg font-semibold text-gray-800 mb-4">
            {translations.fixer_controls || 'Fixer Controls'}
          </h4>
          {selectedJobId ? (
            <JobTrackingControls 
              jobId={selectedJobId}
              onTrackingUpdate={(data) => console.log('Tracking update:', data)}
            />
          ) : (
            <div className="bg-gray-50 p-8 rounded-lg text-center">
              <div className="text-gray-400 mb-2">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                </svg>
              </div>
              <p className="text-gray-500">
                {translations.select_job_first || 'Please select a job to start tracking'}
              </p>
            </div>
          )}
        </div>

        <div>
          <h4 className="text-lg font-semibold text-gray-800 mb-4">
            {translations.client_view || 'Client View'}
          </h4>
          {selectedJobId ? (
            <JobTrackingStatus jobId={selectedJobId} />
          ) : (
            <div className="bg-gray-50 p-8 rounded-lg text-center">
              <div className="text-gray-400 mb-2">
                <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </div>
              <p className="text-gray-500">
                {translations.tracking_status_placeholder || 'Tracking status will appear here'}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  const renderReputation = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          {translations.select_fixer || 'Select Fixer for Reputation'}
        </h3>
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {translations.choose_fixer || 'Choose Fixer:'}
            </label>
            <select
              value={selectedFixerId}
              onChange={(e) => setSelectedFixerId(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
            >
              <option value="">{translations.select_fixer_option || 'Select a fixer...'}</option>
              {sampleFixers.map(fixer => (
                <option key={fixer.id} value={fixer.id}>
                  {fixer.name} - {fixer.service}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {selectedFixerId ? (
        <FixerReputationDashboard fixerId={selectedFixerId} />
      ) : (
        <div className="bg-white p-8 rounded-lg shadow-md text-center">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
            </svg>
          </div>
          <h4 className="text-lg font-medium text-gray-800 mb-2">
            {translations.reputation_dashboard || 'Reputation Dashboard'}
          </h4>
          <p className="text-gray-500 mb-4">
            {translations.select_fixer_reputation || 'Select a fixer to view their reputation, badges, and tier progression.'}
          </p>
        </div>
      )}
    </div>
  );

  const renderAnalytics = () => (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold text-gray-800 mb-4">
          {translations.phase3_analytics || 'Phase 3 Analytics'}
        </h3>
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-3xl font-bold text-blue-600">12</div>
            <div className="text-sm text-blue-700 font-medium">
              {translations.active_tracking || 'Active Tracking Sessions'}
            </div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-3xl font-bold text-purple-600">89%</div>
            <div className="text-sm text-purple-700 font-medium">
              {translations.satisfaction_rate || 'Satisfaction Rate'}
            </div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-3xl font-bold text-green-600">246</div>
            <div className="text-sm text-green-700 font-medium">
              {translations.ai_conversations || 'AI Conversations'}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h4 className="text-md font-semibold text-gray-800 mb-4">
          {translations.feature_usage || 'Feature Usage'}
        </h4>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>{translations.real_time_tracking || 'Real-Time Tracking'}</span>
              <span>85%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full" style={{ width: '85%' }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>{translations.gamification || 'Gamification'}</span>
              <span>72%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-purple-600 h-2 rounded-full" style={{ width: '72%' }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span>{translations.ai_assistant || 'AI Assistant'}</span>
              <span>93%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="bg-green-600 h-2 rounded-full" style={{ width: '93%' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {translations.phase3_dashboard || 'Phase 3: Automation & Engagement'}
        </h1>
        <p className="text-gray-600">
          {translations.phase3_subtitle || 'Advanced features for real-time tracking, gamification, and AI assistance'}
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Content */}
      <div>
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'tracking' && renderTracking()}
        {activeTab === 'reputation' && renderReputation()}
        {activeTab === 'analytics' && renderAnalytics()}
      </div>

      {/* AI Chat Assistant */}
      <AIChatAssistant isOpen={showAIChat} onClose={() => setShowAIChat(false)} />
      
      {!showAIChat && (
        <AIChatButton onClick={() => setShowAIChat(true)} />
      )}
    </div>
  );
};

export default Phase3Dashboard;