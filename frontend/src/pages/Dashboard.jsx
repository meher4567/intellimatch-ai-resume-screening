import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Upload, Briefcase, Search, TrendingUp, Users, Clock } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, LoadingSpinner, Button, Badge } from '../components';
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
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome back! Here's what's happening today.</p>
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
          color="orange"
          trend="up"
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Card title="Resume Activity (Last 7 Days)">
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={trendingData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="resumes" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Match Success Rate">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={trendingData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="matches" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Recent Activity">
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

        <Card title="Quick Actions">
          <div className="grid grid-cols-1 gap-4">
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
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500'
  };
  
  const trendColor = trend === 'up' ? 'text-green-600' : 'text-red-600';

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-gray-600 text-sm mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-800 mb-2">{value}</p>
          {change && (
            <Badge variant="success" size="sm" className={trendColor}>
              {change} from last week
            </Badge>
          )}
        </div>
        <div className={`${colorClasses[color]} text-white w-14 h-14 rounded-xl flex items-center justify-center`}>
          <Icon className="w-7 h-7" />
        </div>
      </div>
    </Card>
  );
}

function ActivityItem({ icon: Icon, title, time }) {
  return (
    <div className="flex items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
        <Icon className="w-5 h-5 text-blue-600" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-800 truncate">{title}</p>
        <p className="text-sm text-gray-500">{time}</p>
      </div>
    </div>
  );
}

function QuickActionCard({ icon: Icon, title, description, onClick }) {
  return (
    <button 
      onClick={onClick}
      className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-lg p-4 text-left hover:shadow-md hover:scale-105 transition-all border border-blue-100"
    >
      <div className="flex items-center mb-2">
        <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center mr-3 shadow-sm">
          <Icon className="w-5 h-5 text-blue-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
      </div>
      <p className="text-sm text-gray-600">{description}</p>
    </button>
  );
}

export default Dashboard;
