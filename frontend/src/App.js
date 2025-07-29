import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { LanguageProvider } from "./contexts/LanguageContext";
import Header from "./components/Layout/Header";
import Navigation from "./components/Layout/Navigation";
import Footer from "./components/Layout/Footer";
import OfflineIndicator from "./components/Common/OfflineIndicator";
import LoginForm from "./components/Auth/LoginForm";
import SignupForm from "./components/Auth/SignupForm";
import Dashboard from "./components/Dashboard/Dashboard";
import JobList from "./components/Jobs/JobList";
import CreateJob from "./components/Jobs/CreateJob";
import FixerList from "./components/Fixers/FixerList";
import LearningPlatform from "./components/Learning/LearningPlatform";
import SMSInterface from "./components/SMS/SMSInterface";
import B2BPortal from "./components/Enterprise/B2BPortal";
import PaymentOptions from "./components/Payment/PaymentOptions";
import Profile from "./components/Profile/Profile";
import AdminDashboard from "./components/Admin/AdminDashboard";

// Protected Route component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    console.log('ProtectedRoute: User not authenticated, redirecting to login');
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Public Route component (for login/signup pages)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  if (isAuthenticated) {
    console.log('PublicRoute: User authenticated, redirecting to dashboard');
    return <Navigate to="/" replace />;
  }
  
  return children;
};

// Layout component for authenticated pages
const Layout = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      <Navigation />
      <OfflineIndicator />
      <main className="container mx-auto px-4 py-8 flex-grow">
        {children}
      </main>
      <Footer />
    </div>
  );
};

// Default Route component
const DefaultRoute = () => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return <Navigate to={isAuthenticated ? "/" : "/login"} replace />;
};

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <div className="App">
          <BrowserRouter>
            <Routes>
              <Route 
                path="/login" 
                element={
                  <PublicRoute>
                    <LoginForm />
                  </PublicRoute>
                } 
              />
              <Route 
                path="/signup" 
                element={
                  <PublicRoute>
                    <SignupForm />
                  </PublicRoute>
                } 
              />
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Dashboard />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/jobs"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <JobList />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/jobs/create"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <CreateJob />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/fixers"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <FixerList />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/learning"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <LearningPlatform />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/sms"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <SMSInterface />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/enterprise"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <B2BPortal />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/payment"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <PaymentOptions 
                        amount={500}
                        description="Sample Payment"
                        onPaymentSuccess={() => {}}
                        onPaymentCancel={() => {}}
                      />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <AdminDashboard />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Profile />
                    </Layout>
                  </ProtectedRoute>
                }
              />
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </BrowserRouter>
        </div>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
