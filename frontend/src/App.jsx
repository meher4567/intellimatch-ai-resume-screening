import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from './pages/Dashboard';
import JobManagement from './pages/JobManagement';
import CandidateMatching from './pages/CandidateMatching';
import InterviewManagement from './pages/InterviewManagement';
import Analytics from './pages/Analytics';
import EmailCenter from './pages/EmailCenter';
import Settings from './pages/Settings';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="flex h-screen bg-gray-100">
          {/* Sidebar */}
          <aside className="w-64 bg-white shadow-lg">
            <div className="p-6">
              <h1 className="text-2xl font-bold text-blue-600">IntelliMatch AI</h1>
              <p className="text-sm text-gray-600">Resume Screening Platform</p>
            </div>
            
            <nav className="mt-6">
              <NavLink to="/" icon="📊">Dashboard</NavLink>
              <NavLink to="/jobs" icon="💼">Job Management</NavLink>
              <NavLink to="/candidates" icon="👥">Candidates</NavLink>
              <NavLink to="/interviews" icon="📅">Interviews</NavLink>
              <NavLink to="/analytics" icon="📈">Analytics</NavLink>
              <NavLink to="/emails" icon="📧">Email Center</NavLink>
              <NavLink to="/settings" icon="⚙️">Settings</NavLink>
            </nav>
          </aside>

          {/* Main Content */}
          <main className="flex-1 overflow-y-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/jobs" element={<JobManagement />} />
              <Route path="/candidates" element={<CandidateMatching />} />
              <Route path="/interviews" element={<InterviewManagement />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/emails" element={<EmailCenter />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

function NavLink({ to, icon, children }) {
  return (
    <Link
      to={to}
      className="flex items-center px-6 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors"
    >
      <span className="mr-3 text-xl">{icon}</span>
      <span>{children}</span>
    </Link>
  );
}

export default App;
