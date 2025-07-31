import React, { Suspense, lazy } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import "./App.css";

// Core Context Providers (always loaded)
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { LanguageProvider } from "./contexts/LanguageContext";

// Core Components (always loaded)
import Layout from "./components/Layout/Layout";
import LoadingSpinner from "./components/Common/LoadingSpinner";

// Lazy-loaded components for code splitting
const LoginForm = lazy(() => import("./components/Auth/LoginForm"));
const SignupForm = lazy(() => import("./components/Auth/SignupForm"));
const Dashboard = lazy(() => import("./components/Dashboard/Dashboard"));
const Profile = lazy(() => import("./components/Profile/Profile"));

// Job Management Components (frequently used, separate chunk)
const CreateJob = lazy(() => import("./components/Jobs/CreateJob"));
const JobList = lazy(() => import("./components/Jobs/JobList"));
const FixerList = lazy(() => import("./components/Fixers/FixerList"));

// Admin Components (admin-only, separate chunk)
const AdminDashboard = lazy(() => import("./components/Admin/AdminDashboard"));
const SmartMatchingDashboard = lazy(() => import("./components/Admin/SmartMatchingDashboard"));
const AdminPhotoVerificationDashboard = lazy(() => import("./components/Admin/AdminPhotoVerificationDashboard"));

// Phase 3 Components (advanced features, separate chunk)
const Phase3Dashboard = lazy(() => import("./components/Phase3/Phase3Dashboard"));
const JobTrackingControls = lazy(() => import("./components/Tracking/JobTrackingControls"));
const JobTrackingStatus = lazy(() => import("./components/Tracking/JobTrackingStatus"));
const FixerReputationDashboard = lazy(() => import("./components/Gamification/FixerReputationDashboard"));
const AIChatAssistant = lazy(() => import("./components/AI/AIChatAssistant"));

// Phase 4 Components (PWA features, separate chunk)
const PWAStatusDashboard = lazy(() => import("./components/PWA/PWAStatusDashboard"));
const PerformanceDashboard = lazy(() => import("./components/Performance/PerformanceDashboard"));

// Business & Enterprise Components (separate chunk)
const BusinessCompliance = lazy(() => import("./components/Business/BusinessCompliance"));
const B2BPortal = lazy(() => import("./components/Enterprise/B2BPortal"));
const LearningPlatform = lazy(() => import("./components/Learning/LearningPlatform"));

// Advanced Workflow Components (separate chunk)
const TermsAcceptance = lazy(() => import("./components/Workflow/TermsAcceptance"));
const EnhancedJobCreation = lazy(() => import("./components/Workflow/EnhancedJobCreation"));
const JobWorkflowStatus = lazy(() => import("./components/Workflow/JobWorkflowStatus"));
const FixerJobBoard = lazy(() => import("./components/Workflow/FixerJobBoard"));
const EnhancedJobCompletion = lazy(() => import("./components/Jobs/EnhancedJobCompletion"));
const DisputeCreation = lazy(() => import("./components/Disputes/DisputeCreation"));

// Communication Components (separate chunk)
const SMSInterface = lazy(() => import("./components/SMS/SMSInterface"));
const VoiceRecorder = lazy(() => import("./components/VoiceRecorder/VoiceRecorder"));

// Payment Components (separate chunk)
const PaymentOptions = lazy(() => import("./components/Payment/PaymentOptions"));
const FixerPaymentManager = lazy(() => import("./components/Payment/FixerPaymentManager"));

// Legal Components (rarely accessed, separate chunk)
const TermsOfService = lazy(() => import("./components/Legal/TermsOfService"));
const PrivacyPolicy = lazy(() => import("./components/Legal/PrivacyPolicy"));

// Create QueryClient with optimized default options
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      cacheTime: 1000 * 60 * 30, // 30 minutes
      retry: 3,
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 30000),
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,
    },
    mutations: {
      retry: 2,
    },
  },
});

// Enhanced Loading Component with better UX
const PageLoadingSpinner = ({ message = "Loading..." }) => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="text-center">
      <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <div className="text-gray-600 font-medium">{message}</div>
      <div className="text-gray-400 text-sm mt-2">FixMate-SA</div>
    </div>
  </div>
);

// Error Boundary for lazy-loaded components
class LazyErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Lazy loading error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
          <div className="text-center max-w-md mx-auto p-6">
            <div className="text-6xl mb-4">😵</div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">
              Oops! Something went wrong
            </h2>
            <p className="text-gray-600 mb-4">
              We're having trouble loading this page. Please try refreshing or go back to the dashboard.
            </p>
            <div className="space-x-3">
              <button
                onClick={() => window.location.reload()}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Refresh Page
              </button>
              <button
                onClick={() => window.location.href = '/'}
                className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
              >
                Go Home
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Optimized Protected Route component with memoization
const ProtectedRoute = React.memo(({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <PageLoadingSpinner message="Authenticating..." />;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
});

// Default route component with lazy loading detection
const DefaultRoute = () => {
  const { isAuthenticated } = useAuth();
  
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }
  
  return <Navigate to="/login" replace />;
};

// Main App Component with optimized routing
function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <LanguageProvider>
        <AuthProvider>
          <Router>
            <div className="App">
              <LazyErrorBoundary>
                <Routes>
                  {/* Authentication Routes - High Priority */}
                  <Route
                    path="/login"
                    element={
                      <Suspense fallback={<PageLoadingSpinner message="Loading login..." />}>
                        <LoginForm />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/signup"
                    element={
                      <Suspense fallback={<PageLoadingSpinner message="Loading signup..." />}>
                        <SignupForm />
                      </Suspense>
                    }
                  />

                  {/* Core App Routes - High Priority */}
                  <Route
                    path="/dashboard"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading dashboard..." />}>
                            <Dashboard />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/profile"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading profile..." />}>
                            <Profile />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />

                  {/* Job Management Routes - High Priority */}
                  <Route
                    path="/jobs/create"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading job creation..." />}>
                            <CreateJob />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/jobs"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading jobs..." />}>
                            <JobList />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/fixers"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading fixers..." />}>
                            <FixerList />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />

                  {/* Enhanced Workflow Routes - Medium Priority */}
                  <Route
                    path="/jobs/workflow/terms"
                    element={
                      <ProtectedRoute>
                        <Suspense fallback={<PageLoadingSpinner message="Loading terms..." />}>
                          <TermsAcceptance />
                        </Suspense>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/jobs/enhanced-create"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading enhanced job creation..." />}>
                            <EnhancedJobCreation />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/jobs/:jobId/status"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading job status..." />}>
                            <JobWorkflowStatus />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/fixer/job-board"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading job board..." />}>
                            <FixerJobBoard />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/jobs/:jobId/complete"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading job completion..." />}>
                            <EnhancedJobCompletion />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/jobs/:jobId/dispute"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading dispute creation..." />}>
                            <DisputeCreation />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />

                  {/* Admin Routes - Admin Only, Lower Priority */}
                  <Route
                    path="/admin"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading admin dashboard..." />}>
                            <AdminDashboard />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/admin/smart-matching"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading smart matching..." />}>
                            <SmartMatchingDashboard />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/admin/photo-verification"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading photo verification..." />}>
                            <AdminPhotoVerificationDashboard />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />

                  {/* Phase 3: Advanced Features - Lower Priority */}
                  <Route
                    path="/phase3"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading Phase 3..." />}>
                            <Phase3Dashboard />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/tracking/:jobId"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading tracking..." />}>
                            <JobTrackingStatus jobId={window.location.pathname.split('/')[2]} />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/reputation/:fixerId"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading reputation..." />}>
                            <FixerReputationDashboard fixerId={window.location.pathname.split('/')[2]} />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />

                  {/* Phase 4: PWA Features */}
                  <Route
                    path="/pwa-status"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading PWA status..." />}>
                            <PWAStatusDashboard />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />

                  {/* Business & Enterprise Features - Lower Priority */}
                  <Route
                    path="/business-compliance"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading business compliance..." />}>
                            <BusinessCompliance />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/enterprise"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading enterprise portal..." />}>
                            <B2BPortal />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/learning"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading learning platform..." />}>
                            <LearningPlatform />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />

                  {/* Communication Features - Lower Priority */}
                  <Route
                    path="/sms"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading SMS interface..." />}>
                            <SMSInterface />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/voice-recorder"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading voice recorder..." />}>
                            <VoiceRecorder />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />

                  {/* Payment Features - Lower Priority */}
                  <Route
                    path="/payment"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading payment options..." />}>
                            <PaymentOptions />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />
                  <Route
                    path="/fixer/payments"
                    element={
                      <ProtectedRoute>
                        <Layout>
                          <Suspense fallback={<PageLoadingSpinner message="Loading payment manager..." />}>
                            <FixerPaymentManager />
                          </Suspense>
                        </Layout>
                      </ProtectedRoute>
                    }
                  />

                  {/* Legal Routes - Lowest Priority */}
                  <Route
                    path="/terms"
                    element={
                      <Suspense fallback={<PageLoadingSpinner message="Loading terms of service..." />}>
                        <TermsOfService />
                      </Suspense>
                    }
                  />
                  <Route
                    path="/privacy"
                    element={
                      <Suspense fallback={<PageLoadingSpinner message="Loading privacy policy..." />}>
                        <PrivacyPolicy />
                      </Suspense>
                    }
                  />

                  {/* Default Route */}
                  <Route path="*" element={<DefaultRoute />} />
                </Routes>
              </LazyErrorBoundary>
            </div>
          </Router>
        </AuthProvider>
      </LanguageProvider>
    </QueryClientProvider>
  );
}

export default App;