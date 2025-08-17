import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import "./App.css";

// FixMate-SA App v2.5.0 - ENVIRONMENT VARIABLE INDEPENDENT - 2025-01-14

// Core Context Providers
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { LanguageProvider } from "./contexts/LanguageContext";

// Core Components - Direct imports (no lazy loading for stability)
import LoginForm from "./components/Auth/LoginForm";
import SignupForm from "./components/Auth/SignupForm";

// Role-specific Auth Components
import ClientLogin from "./components/Auth/ClientLogin";
import FixerLogin from "./components/Auth/FixerLogin";
import AdminLogin from "./components/Auth/AdminLogin";
import ClientSignup from "./components/Auth/ClientSignup";
import FixerSignup from "./components/Auth/FixerSignup";
import Dashboard from "./components/Dashboard/Dashboard";
import Layout from "./components/Layout/Layout";
import ResponsiveLayout from "./components/Layout/ResponsiveLayout";
import ProfessionalLayout from "./components/Layout/ProfessionalLayout";

// Job Management Components
import CreateJob from "./components/Jobs/CreateJob";
import JobList from "./components/Jobs/JobList";
import ClientRateJobs from "./components/Jobs/ClientRateJobs";
import FixerList from "./components/Fixers/FixerList";
import FixerAvailableJobs from "./components/Fixers/FixerAvailableJobs";
import FixerJobNotifications from "./components/Fixers/FixerJobNotifications";
import Profile from "./components/Profile/Profile";

// Admin Components  
import AdminDashboard from "./components/Admin/AdminDashboard";
import AdminLearningAnalytics from "./components/Admin/AdminLearningAnalytics";
import SmartMatchingDashboard from "./components/Admin/SmartMatchingDashboard";
import AdminPhotoVerificationDashboard from "./components/Admin/AdminPhotoVerificationDashboard";

// Business & Enterprise Components
import BusinessCompliance from "./components/Business/BusinessCompliance";
import B2BPortal from "./components/Enterprise/B2BPortal";
import LearningPlatform from "./components/Learning/LearningPlatform";

// Advanced Workflow Components
import TermsAcceptance from "./components/Workflow/TermsAcceptance";
import EnhancedJobCreation from "./components/Workflow/EnhancedJobCreation";
import JobWorkflowStatus from "./components/Workflow/JobWorkflowStatus";
import FixerJobBoard from "./components/Workflow/FixerJobBoard";
import EnhancedJobCompletion from "./components/Jobs/EnhancedJobCompletion";
import DisputeCreation from "./components/Disputes/DisputeCreation";

// Communication Components
import SMSInterface from "./components/SMS/SMSInterface";
import VoiceRecorder from "./components/VoiceRecorder/VoiceRecorder";
import FixerReputationDashboard from "./components/Gamification/FixerReputationDashboard";

// Common Components
import PWAInstallPrompt from "./components/Common/PWAInstallPrompt";

// Payment Components
import PaymentOptions from "./components/Payment/PaymentOptions";
import FixerPaymentManager from "./components/Payment/FixerPaymentManager";

// Legal Components
import TermsOfService from "./components/Legal/TermsOfService";
import PrivacyPolicy from "./components/Legal/PrivacyPolicy";

// Quick Links Pages
import AboutUs from "./components/Pages/AboutUs";
import HowItWorks from "./components/Pages/HowItWorks";
import SafetyTrust from "./components/Pages/SafetyTrust";
import BecomeFixer from "./components/Pages/BecomeFixer";
import HelpCenter from "./components/Pages/HelpCenter";

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <div className="text-gray-600 font-medium">Loading...</div>
        </div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/client-login" replace />;
  }
  
  return children;
};

// Role-based default route component
const DefaultRoute = () => {
  try {
    const { isAuthenticated, getUserRole, loading } = useAuth();
    
    console.log('DefaultRoute: isAuthenticated =', isAuthenticated, 'loading =', loading);
    
    if (loading) {
      return (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <div className="text-gray-600 font-medium">Loading...</div>
          </div>
        </div>
      );
    }
    
    if (!isAuthenticated) {
      console.log('DefaultRoute: Not authenticated, redirecting to /client-login');
      return <Navigate to="/client-login" replace />;
    }
    
    // Role-based routing for authenticated users
    const userRole = getUserRole();
    console.log('DefaultRoute: User role =', userRole);
    
    switch (userRole) {
      case 'admin':
        return <Navigate to="/admin/dashboard" replace />;
      case 'fixer':
        return <Navigate to="/fixer/dashboard" replace />;
      case 'client':
      default:
        return <Navigate to="/client/dashboard" replace />;
    }
  } catch (error) {
    console.error('DefaultRoute error:', error);
    // Fallback if AuthContext fails
    return <Navigate to="/client-login" replace />;
  }
};

// Main App Component with Full Routing
function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <Router>
          <div className="App">
            <Routes>
              {/* Role-specific Authentication Routes */}
              <Route path="/client-login" element={<ClientLogin />} />
              <Route path="/fixer-login" element={<FixerLogin />} />
              <Route path="/fixers-login" element={<FixerLogin />} />
              <Route path="/admin-login" element={<AdminLogin />} />
              <Route path="/client-signup" element={<ClientSignup />} />
              <Route path="/fixer-signup" element={<FixerSignup />} />

              {/* Legacy Authentication Routes - Redirect to client login */}
              <Route path="/login" element={<Navigate to="/client-login" replace />} />
              <Route path="/signup" element={<Navigate to="/client-signup" replace />} />

              {/* Public Routes - Must be before protected routes */}
              <Route path="/terms" element={<TermsOfService />} />
              <Route path="/privacy" element={<PrivacyPolicy />} />
              <Route path="/terms-of-service" element={<TermsOfService />} />
              <Route path="/privacy-policy" element={<PrivacyPolicy />} />
              
              {/* Public Quick Links Pages */}
              <Route path="/about-us" element={<AboutUs />} />
              <Route path="/how-it-works" element={<HowItWorks />} />
              <Route path="/safety-trust" element={<SafetyTrust />} />
              <Route path="/become-fixer" element={<BecomeFixer />} />
              <Route path="/help-center" element={<HelpCenter />} />

              {/* Role-based Dashboard Routes */}
              <Route
                path="/client/dashboard"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <Dashboard />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/fixer/dashboard"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <Dashboard />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/dashboard"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <Dashboard />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/learning-analytics"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <AdminLearningAnalytics />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Admin Panel for admin-specific features */}              
              <Route
                path="/admin/panel"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <AdminDashboard />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Fixer Job Board for available jobs */}
              <Route
                path="/fixer/jobs"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <FixerJobBoard />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Fixer Available Jobs - Direct Route */}
              <Route
                path="/fixer/available-jobs"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <FixerAvailableJobs />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Fixer Notifications - Direct Route */}
              <Route
                path="/fixer/notifications"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <FixerJobNotifications />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Legacy Dashboard Route - Redirect based on role */}
              <Route
                path="/dashboard"
                element={<Navigate to="/" replace />}
              />

              {/* Core App Routes */}
              {/* Role-based Profile Routes */}
              <Route
                path="/client/profile"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <Profile />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/client/rate-jobs"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <ClientRateJobs />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/client/business-compliance"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <BusinessCompliance />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/client/enterprise"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <B2BPortal />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/business/compliance"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <BusinessCompliance />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/fixer/profile"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <Profile />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/profile"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <Profile />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              
              {/* Legacy Profile Route - Redirect to role-based */}
              <Route path="/profile" element={<Navigate to="/" replace />} />

              {/* Role-based Learning Routes */}
              <Route
                path="/client/learning"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <LearningPlatform />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/fixer/learning"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <LearningPlatform />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/learning"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <LearningPlatform />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Role-based Payment Routes */}
              <Route
                path="/client/payment"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <PaymentOptions />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/payment"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <PaymentOptions />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Legacy Route Redirects - Only keep non-conflicting ones */}

              {/* Role-based Business Compliance Routes */}
              <Route
                path="/admin/business-compliance"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <BusinessCompliance />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/fixer/business-compliance"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <BusinessCompliance />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Role-based SMS Routes */}
              <Route
                path="/admin/sms"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <SMSInterface />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Role-based Enterprise Routes */}
              <Route
                path="/admin/enterprise"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <B2BPortal />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Additional Legacy Route Redirects - Cleaned up duplicates */}

              {/* Job Management Routes */}
              <Route
                path="/jobs/create"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <CreateJob />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/jobs"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <JobList />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/fixers"
                element={
                    <ProfessionalLayout>
                      <FixerList />
                    </ProfessionalLayout>
                }
              />

              {/* Enhanced Workflow Routes */}
              <Route
                path="/jobs/workflow/terms"
                element={
                  <ProtectedRoute>
                    <TermsAcceptance />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/jobs/enhanced-create"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <EnhancedJobCreation />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/jobs/:jobId/status"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <JobWorkflowStatus />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/fixer/job-board"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <FixerJobBoard />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/jobs/:jobId/complete"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <EnhancedJobCompletion />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/jobs/:jobId/dispute"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <DisputeCreation />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Admin Routes */}
              <Route
                path="/admin"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <AdminDashboard />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/smart-matching"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <SmartMatchingDashboard />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/photo-verification"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <AdminPhotoVerificationDashboard />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Admin-specific routes */}
              <Route
                path="/admin/business-compliance"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <BusinessCompliance />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin/enterprise"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <B2BPortal />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Fixer-specific routes */}
              <Route
                path="/fixer/reputation"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <FixerReputationDashboard />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/jobs/list"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <JobList />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Business & Enterprise Features */}
              <Route
                path="/business-compliance"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <BusinessCompliance />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/enterprise"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <B2BPortal />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/learning"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <LearningPlatform />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Communication Features */}
              <Route
                path="/sms"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <SMSInterface />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/voice-recorder"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <VoiceRecorder />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Fixer Payment Management */}
              <Route
                path="/fixer/payment"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <FixerPaymentManager />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/fixer/payments"
                element={
                  <ProtectedRoute>
                    <ProfessionalLayout>
                      <FixerPaymentManager />
                    </ProfessionalLayout>
                  </ProtectedRoute>
                }
              />

              {/* Direct Root Route - Force redirect to client-login */}
              <Route path="/" element={<Navigate to="/client-login" replace />} />
              
              {/* Default Route - catch all other paths */}
              <Route path="*" element={<DefaultRoute />} />
            </Routes>
            
            {/* PWA Install Prompt - Available globally */}
            <PWAInstallPrompt />
          </div>
        </Router>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;