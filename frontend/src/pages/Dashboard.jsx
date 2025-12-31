import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Upload, Briefcase, Search, TrendingUp, Users, Clock, Target } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, LoadingSpinner, Button, Badge, StatCard } from '../components';
import api from '../api/config';

function Dashboard() {
  const navigate = useNavigate();
  
  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const response = await api.get('/api/v1/analytics/stats');
      return response.data;
    },
    retry: 2,
    staleTime: 30000,
  });

  const { data: analyticsData, error: analyticsError } = useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      const response = await api.get('/api/v1/analytics/dashboard');
      return response.data;
    },
    retry: 2,
    staleTime: 30000,
  });
  
  const { data: recentActivity } = useQuery({
    queryKey: ['recent-activity'],
    queryFn: async () => {
      // TODO: Backend doesn't have recent-activity endpoint yet
      // Using mock data for now
      return [];
    },
    retry: 1,
  });

  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="lg" text="Loading dashboard..." />
      </div>
    );
  }

  if (statsError || analyticsError) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center bg-red-50 p-8 rounded-lg">
          <div className="text-4xl mb-4">⚠️</div>
          <div className="text-xl text-red-600 mb-2">Failed to load dashboard</div>
          <p className="text-gray-600">Make sure the backend server is running</p>
          <button 
            onClick={() => window.location.reload()} 
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Mock trending data for charts
  const trendingData = [
    { name: 'Mon', resumes: 12, matches: 8 },
    { name: 'Tue', resumes: 19, matches: 14 },
    { name: 'Wed', resumes: 15, matches: 11 },
    { name: 'Thu', resumes: 22, matches: 16 },
    { name: 'Fri', resumes: 28, matches: 20 },
    { name: 'Sat', resumes: 8, matches: 5 },
    { name: 'Sun', resumes: 5, matches: 3 },
  ];

  return (
    <div className="p-8 min-h-screen animate-fade-in">
      <div className="mb-8 animate-fade-in-down">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">Dashboard</h1>
        <p className="text-gray-600 text-lg">Welcome back! Here's what's happening today. ✨</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard 
          title="Total Resumes" 
          value={stats?.total_resumes || 0}
          change="+12%"
          icon={Users}
          color="blue"
          trend="up"
        />
        <StatCard 
          title="Active Jobs" 
          value={analyticsData?.active_jobs || 0}
          change="+5%"
          icon={Briefcase}
          color="green"
          trend="up"
        />
        <StatCard 
          title="Total Matches" 
          value={stats?.total_matches || 0}
          change="+23%"
          icon={TrendingUp}
          color="purple"
          trend="up"
        />
        <StatCard 
          title="Avg Match Score" 
          value={analyticsData?.avg_match_score || "87%"}
          change="+2%"
          icon={Search}
          color="indigo"
          trend="up"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card title="📈 Resume Activity (Last 7 Days)" hover={false}>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trendingData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(255, 255, 255, 0.95)', 
                  backdropFilter: 'blur(10px)',
                  border: 'none',
                  borderRadius: '12px',
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="resumes" 
                stroke="#6366f1" 
                strokeWidth={3}
                dot={{ fill: '#6366f1', r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card title="🎯 Match Success Rate" hover={false}>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={trendingData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="name" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(255, 255, 255, 0.95)', 
                  backdropFilter: 'blur(10px)',
                  border: 'none',
                  borderRadius: '12px',
                  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)'
                }}
              />
              <Bar 
                dataKey="matches" 
                fill="url(#colorGradient)" 
                radius={[8, 8, 0, 0]}
              />
              <defs>
                <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#8b5cf6" stopOpacity={1}/>
                  <stop offset="100%" stopColor="#ec4899" stopOpacity={0.8}/>
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="⏱️ Recent Activity" hover={false}>
          <div className="space-y-3">
            {recentActivity && recentActivity.length > 0 ? (
              recentActivity.slice(0, 5).map((activity, index) => (
                <ActivityItem 
                  key={index}
                  icon={Clock}
                  title={activity.title}
                  time={activity.time}
                />
              ))
            ) : (
              <div className="space-y-3">
                <ActivityItem icon={Users} title="John Doe's resume parsed" time="2 hours ago" />
                <ActivityItem icon={Briefcase} title="Software Engineer job created" time="3 hours ago" />
                <ActivityItem icon={TrendingUp} title="5 new matches found" time="4 hours ago" />
                <ActivityItem icon={Clock} title="Interview scheduled with Jane" time="5 hours ago" />
              </div>
            )}
          </div>
        </Card>

        <Card title="⚡ Quick Actions" hover={false}>
          <div className="grid grid-cols-1 gap-4">
            <QuickActionCard 
              icon={Target}
              title="Resume Analyzer" 
              description="Upload one resume & see extracted details + quality score"
              onClick={() => navigate('/analyzer')}
            />
            <QuickActionCard 
              icon={Upload}
              title="Upload Resumes" 
              description="Upload and parse new resumes with AI"
              onClick={() => navigate('/upload')}
            />
            <QuickActionCard 
              icon={Briefcase}
              title="Create Job" 
              description="Post a new job opening"
              onClick={() => navigate('/jobs')}
            />
            <QuickActionCard 
              icon={Search}
              title="Find Matches" 
              description="Match candidates to jobs instantly"
              onClick={() => navigate('/candidates')}
            />
          </div>
        </Card>
      </div>
    </div>
  );
}

function StatCard({ title, value, change, icon: Icon, color, trend }) {
  // This is now replaced by the imported StatCard component
  // Keeping for backward compatibility but not used
  return null;
}

export default Dashboard;
