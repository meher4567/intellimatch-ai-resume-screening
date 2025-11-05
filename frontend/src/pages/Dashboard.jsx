import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/config';

function Dashboard() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const response = await api.get('/api/v1/stats');
      return response.data;
    },
    retry: 2,
    staleTime: 30000, // 30 seconds
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

  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-4xl mb-4">⏳</div>
          <div className="text-xl text-gray-600">Loading dashboard...</div>
        </div>
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

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard 
          title="Total Resumes" 
          value={stats?.total_resumes || 0} 
          icon="📄"
          color="blue"
        />
        <StatCard 
          title="Active Jobs" 
          value={analyticsData?.active_jobs || 0} 
          icon="💼"
          color="green"
        />
        <StatCard 
          title="Total Matches" 
          value={stats?.total_matches || 0} 
          icon="🎯"
          color="purple"
        />
        <StatCard 
          title="Interviews Scheduled" 
          value={analyticsData?.scheduled_interviews || 0} 
          icon="📅"
          color="orange"
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Resumes</h2>
          <div className="space-y-3">
            <ActivityItem icon="📄" title="John Doe's resume uploaded" time="2 hours ago" />
            <ActivityItem icon="📄" title="Jane Smith's resume uploaded" time="3 hours ago" />
            <ActivityItem icon="📄" title="Bob Johnson's resume uploaded" time="5 hours ago" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Upcoming Interviews</h2>
          <div className="space-y-3">
            <ActivityItem icon="📅" title="Interview with Alice Brown" time="Tomorrow at 10:00 AM" />
            <ActivityItem icon="📅" title="Interview with Charlie Davis" time="Tomorrow at 2:00 PM" />
            <ActivityItem icon="📅" title="Interview with Eva Wilson" time="Day after tomorrow" />
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <QuickActionCard icon="📤" title="Upload Resume" description="Upload and parse new resumes" />
          <QuickActionCard icon="➕" title="Create Job" description="Post a new job opening" />
          <QuickActionCard icon="🔍" title="Find Matches" description="Match candidates to jobs" />
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500'
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm">{title}</p>
          <p className="text-3xl font-bold mt-2">{value}</p>
        </div>
        <div className={`${colorClasses[color]} text-white w-12 h-12 rounded-lg flex items-center justify-center text-2xl`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function ActivityItem({ icon, title, time }) {
  return (
    <div className="flex items-center p-3 bg-gray-50 rounded-lg">
      <span className="text-2xl mr-3">{icon}</span>
      <div className="flex-1">
        <p className="font-medium text-gray-800">{title}</p>
        <p className="text-sm text-gray-600">{time}</p>
      </div>
    </div>
  );
}

function QuickActionCard({ icon, title, description }) {
  return (
    <button className="bg-white rounded-lg shadow p-6 text-left hover:shadow-lg transition-shadow">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold mb-1">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </button>
  );
}

export default Dashboard;
