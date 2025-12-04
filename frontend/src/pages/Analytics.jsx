import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { BarChart3, TrendingUp, Users, Briefcase, Award, Download, Calendar, Filter } from 'lucide-react';
import { Card, Button, Badge, LoadingSpinner, EmptyState } from '../components';
import api from '../api/config';

function Analytics() {
  const [timeRange, setTimeRange] = useState('30'); // days
  const [selectedMetric, setSelectedMetric] = useState('all');

  // Fetch analytics data
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics', timeRange],
    queryFn: async () => {
      // Since we don't have a specific analytics endpoint, we'll fetch and aggregate data
      const [resumes, jobs, matches] = await Promise.all([
        api.get('/api/v1/resumes/').then(r => r.data),
        api.get('/api/v1/jobs/').then(r => r.data),
        // For matches, we'll need to simulate or use available data
        Promise.resolve([])
      ]);
      return { resumes, jobs, matches };
    },
  });

  // Mock data for demonstration (replace with real data when available)
  const skillTrendData = [
    { skill: 'Python', count: 45, change: 12 },
    { skill: 'JavaScript', count: 38, change: 8 },
    { skill: 'React', count: 35, change: 15 },
    { skill: 'AWS', count: 32, change: 5 },
    { skill: 'Machine Learning', count: 28, change: 20 },
    { skill: 'SQL', count: 42, change: -3 },
    { skill: 'Docker', count: 25, change: 10 },
    { skill: 'Node.js', count: 30, change: 7 },
  ];

  const qualityDistribution = [
    { name: 'Tier S (90-100)', value: 12, color: '#9333EA' },
    { name: 'Tier A (80-89)', value: 28, color: '#10B981' },
    { name: 'Tier B (70-79)', value: 35, color: '#3B82F6' },
    { name: 'Tier C (60-69)', value: 18, color: '#F59E0B' },
    { name: 'Tier D (50-59)', value: 7, color: '#EF4444' },
  ];

  const hiringFunnelData = [
    { stage: 'Resumes Received', count: 150, percentage: 100 },
    { stage: 'Screened', count: 120, percentage: 80 },
    { stage: 'Interviews', count: 45, percentage: 30 },
    { stage: 'Offers', count: 15, percentage: 10 },
    { stage: 'Hired', count: 12, percentage: 8 },
  ];

  const monthlyTrends = [
    { month: 'Jun', resumes: 45, matches: 32, hires: 5 },
    { month: 'Jul', resumes: 52, matches: 38, hires: 6 },
    { month: 'Aug', resumes: 48, matches: 35, hires: 4 },
    { month: 'Sep', resumes: 65, matches: 48, hires: 8 },
    { month: 'Oct', resumes: 58, matches: 42, hires: 7 },
    { month: 'Nov', resumes: 72, matches: 55, hires: 9 },
  ];

  const timeToHireData = [
    { range: '0-7 days', count: 3 },
    { range: '8-14 days', count: 5 },
    { range: '15-21 days', count: 8 },
    { range: '22-30 days', count: 12 },
    { range: '31+ days', count: 6 },
  ];

  const handleExport = () => {
    // Export analytics data (implement with real export logic)
    const dataStr = JSON.stringify({
      skillTrends: skillTrendData,
      qualityDistribution,
      hiringFunnel: hiringFunnelData,
      monthlyTrends,
      timeToHire: timeToHireData,
      exportDate: new Date().toISOString(),
    }, null, 2);
    
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = `analytics_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  if (isLoading) {
    return (
      <div className="p-8">
        <LoadingSpinner size="lg" text="Loading analytics..." />
      </div>
    );
  }

  const totalResumes = analytics?.resumes?.length || 0;
  const totalJobs = analytics?.jobs?.length || 0;
  const activeJobs = analytics?.jobs?.filter(j => j.status === 'active').length || 0;

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center">
            <BarChart3 className="mr-3 text-blue-600" />
            Analytics Dashboard
          </h1>
          <div className="flex space-x-3">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none"
            >
              <option value="7">Last 7 days</option>
              <option value="30">Last 30 days</option>
              <option value="90">Last 90 days</option>
              <option value="365">Last year</option>
            </select>
            <Button onClick={handleExport} icon={Download} variant="outline">
              Export Data
            </Button>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Total Resumes</p>
                <p className="text-3xl font-bold text-gray-900">{totalResumes}</p>
                <p className="text-sm text-green-600 mt-1">↑ 12% vs last period</p>
              </div>
              <Users className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Active Jobs</p>
                <p className="text-3xl font-bold text-gray-900">{activeJobs}</p>
                <p className="text-sm text-green-600 mt-1">↑ 5% vs last period</p>
              </div>
              <Briefcase className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Avg Match Score</p>
                <p className="text-3xl font-bold text-gray-900">78.5</p>
                <p className="text-sm text-green-600 mt-1">↑ 3% vs last period</p>
              </div>
              <Award className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 mb-1">Time to Hire</p>
                <p className="text-3xl font-bold text-gray-900">21d</p>
                <p className="text-sm text-red-600 mt-1">↓ 2 days</p>
              </div>
              <Calendar className="w-12 h-12 text-orange-500 opacity-20" />
            </div>
          </Card>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Skill Trends */}
        <Card title="Trending Skills">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={skillTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="skill" angle={-45} textAnchor="end" height={100} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3B82F6" />
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-gray-600">
              Most in-demand skills in candidate pool
            </p>
          </div>
        </Card>

        {/* Quality Distribution */}
        <Card title="Resume Quality Distribution">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={qualityDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percentage, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {qualityDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-gray-600">
              Distribution of resume quality scores across tiers
            </p>
          </div>
        </Card>

        {/* Monthly Trends */}
        <Card title="Monthly Activity Trends">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyTrends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="resumes" stroke="#3B82F6" strokeWidth={2} name="Resumes" />
              <Line type="monotone" dataKey="matches" stroke="#10B981" strokeWidth={2} name="Matches" />
              <Line type="monotone" dataKey="hires" stroke="#9333EA" strokeWidth={2} name="Hires" />
            </LineChart>
          </ResponsiveContainer>
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-gray-600">
              6-month trend of recruitment activities
            </p>
          </div>
        </Card>

        {/* Time to Hire */}
        <Card title="Time to Hire Distribution">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={timeToHireData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="range" type="category" width={100} />
              <Tooltip />
              <Bar dataKey="count" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-gray-600">
              Average time from application to hiring decision
            </p>
          </div>
        </Card>
      </div>

      {/* Hiring Funnel */}
      <Card title="Hiring Funnel Analysis">
        <div className="space-y-4">
          {hiringFunnelData.map((stage, index) => (
            <div key={stage.stage}>
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium text-gray-700">{stage.stage}</span>
                <span className="text-sm text-gray-600">
                  {stage.count} candidates ({stage.percentage}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-4">
                <div
                  className="h-4 rounded-full transition-all"
                  style={{
                    width: `${stage.percentage}%`,
                    backgroundColor: `hsl(${220 - index * 20}, 70%, 50%)`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>
        <div className="mt-6 pt-4 border-t">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-blue-600">80%</p>
              <p className="text-sm text-gray-600">Screen Rate</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-green-600">30%</p>
              <p className="text-sm text-gray-600">Interview Rate</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-600">8%</p>
              <p className="text-sm text-gray-600">Hire Rate</p>
            </div>
          </div>
        </div>
      </Card>

      {/* Insights Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
        <Card>
          <div className="flex items-start space-x-3">
            <TrendingUp className="w-6 h-6 text-green-600 mt-1" />
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">Top Insight</h3>
              <p className="text-sm text-gray-600">
                Machine Learning skills increased by 20% this month, showing growing demand in tech roles.
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start space-x-3">
            <Award className="w-6 h-6 text-blue-600 mt-1" />
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">Quality Improvement</h3>
              <p className="text-sm text-gray-600">
                Average resume quality improved by 8%, with more Tier A and S candidates.
              </p>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-start space-x-3">
            <Calendar className="w-6 h-6 text-orange-600 mt-1" />
            <div>
              <h3 className="font-semibold text-gray-900 mb-1">Faster Hiring</h3>
              <p className="text-sm text-gray-600">
                Time to hire decreased by 2 days, improving efficiency in candidate selection.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default Analytics;
