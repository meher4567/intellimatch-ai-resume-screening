import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { LayoutDashboard, Briefcase, Users, Calendar, BarChart3, Mail, Settings as SettingsIcon, Upload } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import JobManagement from './pages/JobManagement';
import CandidateMatching from './pages/CandidateMatching';
import InterviewManagement from './pages/InterviewManagement';
import Analytics from './pages/Analytics';
import EmailCenter from './pages/EmailCenter';
import Settings from './pages/Settings';
import ResumeUpload from './pages/ResumeUpload';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppContent />
      </Router>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 4000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </QueryClientProvider>
  );
}

function AppContent() {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-lg flex-shrink-0">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            IntelliMatch AI
          </h1>
          <p className="text-sm text-gray-600 mt-1">Powered by ML</p>
        </div>
        
        <nav className="mt-4">
          <NavLink to="/" icon={LayoutDashboard}>Dashboard</NavLink>
          <NavLink to="/upload" icon={Upload}>Upload Resumes</NavLink>
          <NavLink to="/jobs" icon={Briefcase}>Job Management</NavLink>
          <NavLink to="/candidates" icon={Users}>Candidates</NavLink>
          <NavLink to="/interviews" icon={Calendar}>Interviews</NavLink>
          <NavLink to="/analytics" icon={BarChart3}>Analytics</NavLink>
          <NavLink to="/emails" icon={Mail}>Email Center</NavLink>
          <NavLink to="/settings" icon={SettingsIcon}>Settings</NavLink>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<ResumeUpload />} />
          <Route path="/jobs" element={<JobManagement />} />
          <Route path="/candidates" element={<CandidateMatching />} />
          <Route path="/interviews" element={<InterviewManagement />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/emails" element={<EmailCenter />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  );
}

function NavLink({ to, icon: Icon, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link
      to={to}
      className={`flex items-center px-6 py-3 transition-all duration-200 ${
        isActive 
          ? 'bg-blue-50 text-blue-600 border-r-4 border-blue-600 font-medium' 
          : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'
      }`}
    >
      <Icon className="mr-3 w-5 h-5" />
      <span>{children}</span>
    </Link>
  );
}

export default App;
