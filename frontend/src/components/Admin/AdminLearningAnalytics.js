import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const AdminLearningAnalytics = () => {
  const { user } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [aiInsights, setAiInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user?.role === 'admin') {
      fetchLearningAnalytics();
    }
  }, [user]);

  const fetchLearningAnalytics = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/learning/analytics`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('fixmate_token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setAnalytics(data.analytics);
          setAiInsights(data.ai_insights);
        } else {
          setError('Failed to load analytics');
        }
      } else {
        setError(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (err) {
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (user?.role !== 'admin') {
    return (
      <div className="p-6 text-center">
        <h2 className="text-xl font-semibold text-red-600">Access Denied</h2>
        <p className="text-gray-600">Admin access required to view learning analytics.</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-6 text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p className="mt-4 text-gray-600">Loading learning analytics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center">
        <h2 className="text-xl font-semibold text-red-600">Error Loading Analytics</h2>
        <p className="text-gray-600">{error}</p>
        <button 
          onClick={fetchLearningAnalytics}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-6">
        <h1 className="text-3xl font-bold mb-2">📊 Learning Analytics Dashboard</h1>
        <p className="text-blue-100">
          AI-powered insights into platform learning trends and user engagement
        </p>
      </div>

      {/* Overall Statistics */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold mb-4">📈 Platform Overview</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-blue-600">{analytics?.overall_stats?.total_learners || 0}</div>
            <div className="text-sm text-blue-700">Total Learners</div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-green-600">{analytics?.overall_stats?.total_courses_started || 0}</div>
            <div className="text-sm text-green-700">Courses Started</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-purple-600">{analytics?.overall_stats?.total_courses_completed || 0}</div>
            <div className="text-sm text-purple-700">Completed</div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-yellow-600">{analytics?.overall_stats?.total_learning_hours || 0}h</div>
            <div className="text-sm text-yellow-700">Learning Hours</div>
          </div>
          <div className="bg-indigo-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-indigo-600">{analytics?.overall_stats?.total_certificates || 0}</div>
            <div className="text-sm text-indigo-700">Certificates</div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg text-center">
            <div className="text-2xl font-bold text-red-600">{analytics?.overall_stats?.avg_completion_rate || 0}%</div>
            <div className="text-sm text-red-700">Completion Rate</div>
          </div>
        </div>
      </div>

      {/* AI Insights */}
      {aiInsights && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold mb-4">🤖 AI-Powered Insights</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Key Findings */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="font-semibold text-blue-900 mb-3">🔍 Key Findings</h3>
              <ul className="space-y-2">
                {aiInsights.key_findings?.map((finding, index) => (
                  <li key={index} className="text-sm text-blue-800 flex items-start">
                    <span className="mr-2">•</span>
                    <span>{finding}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Recommendations */}
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="font-semibold text-green-900 mb-3">💡 Recommendations</h3>
              <ul className="space-y-2">
                {aiInsights.recommendations?.map((rec, index) => (
                  <li key={index} className="text-sm text-green-800 flex items-start">
                    <span className="mr-2">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Trends */}
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="font-semibold text-purple-900 mb-3">📈 Trends</h3>
              <ul className="space-y-2">
                {aiInsights.trends?.map((trend, index) => (
                  <li key={index} className="text-sm text-purple-800 flex items-start">
                    <span className="mr-2">•</span>
                    <span>{trend}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Opportunities */}
            <div className="bg-orange-50 p-4 rounded-lg">
              <h3 className="font-semibold text-orange-900 mb-3">🚀 Opportunities</h3>
              <ul className="space-y-2">
                {aiInsights.opportunities?.map((opp, index) => (
                  <li key={index} className="text-sm text-orange-800 flex items-start">
                    <span className="mr-2">•</span>
                    <span>{opp}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          
          {aiInsights.generated_at && (
            <div className="mt-4 text-xs text-gray-500 text-center">
              AI insights generated at: {new Date(aiInsights.generated_at).toLocaleString()}
            </div>
          )}
        </div>
      )}

      {/* Top Courses */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold mb-4">🏆 Top Performing Courses</h2>
        {analytics?.top_courses?.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Course</th>
                  <th className="text-left py-2">Platform</th>
                  <th className="text-center py-2">Enrollments</th>
                  <th className="text-center py-2">Avg Progress</th>
                  <th className="text-center py-2">Completions</th>
                  <th className="text-center py-2">Success Rate</th>
                </tr>
              </thead>
              <tbody>
                {analytics.top_courses.map((course, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="py-3 font-medium">{course.course_title}</td>
                    <td className="py-3">
                      <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                        {course.course_platform}
                      </span>
                    </td>
                    <td className="py-3 text-center">{course.enrollments}</td>
                    <td className="py-3 text-center">{course.avg_progress}%</td>
                    <td className="py-3 text-center">{course.completions}</td>
                    <td className="py-3 text-center">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        course.completion_rate >= 50 ? 'bg-green-100 text-green-800' :
                        course.completion_rate >= 25 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {course.completion_rate}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No course data available yet.</p>
        )}
      </div>

      {/* User Engagement by Role */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold mb-4">👥 User Engagement by Role</h2>
        {analytics?.user_engagement?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {analytics.user_engagement.map((role, index) => (
              <div key={index} className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-900 capitalize">{role.role}s</h3>
                <div className="mt-2 space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>Active Learners:</span>
                    <span className="font-medium">{role.active_learners}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Avg Courses:</span>
                    <span className="font-medium">{role.avg_courses_per_user}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Avg Hours:</span>
                    <span className="font-medium">{role.avg_hours_per_user}h</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No user engagement data available yet.</p>
        )}
      </div>

      {/* Platform Statistics */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h2 className="text-xl font-semibold mb-4">📚 Learning Platform Performance</h2>
        {analytics?.platform_stats?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {analytics.platform_stats.map((platform, index) => (
              <div key={index} className="bg-gradient-to-r from-blue-50 to-purple-50 p-4 rounded-lg border">
                <h3 className="font-semibold text-gray-900">{platform.platform}</h3>
                <div className="mt-2 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Enrollments:</span>
                    <span className="font-medium">{platform.enrollments}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Completions:</span>
                    <span className="font-medium">{platform.completions}</span>
                  </div>
                  <div className="mt-2">
                    <div className="flex justify-between text-xs mb-1">
                      <span>Success Rate</span>
                      <span>{platform.completion_rate}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${platform.completion_rate}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-4">No platform statistics available yet.</p>
        )}
      </div>

      {/* Refresh Button */}
      <div className="text-center">
        <button
          onClick={fetchLearningAnalytics}
          className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700"
        >
          🔄 Refresh Analytics
        </button>
      </div>
    </div>
  );
};

export default AdminLearningAnalytics;