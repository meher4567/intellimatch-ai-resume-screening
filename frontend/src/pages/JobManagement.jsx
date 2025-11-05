import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/config';

function JobManagement() {
  const [showCreateForm, setShowCreateForm] = useState(false);

  const { data: jobs, isLoading, error } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      const response = await api.get('/api/v1/jobs/');
      return response.data;
    },
    retry: 2,
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <div className="text-4xl mb-4">⏳</div>
          <div className="text-xl text-gray-600">Loading jobs...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="text-center bg-red-50 p-8 rounded-lg">
          <div className="text-4xl mb-4">⚠️</div>
          <div className="text-xl text-red-600 mb-2">Failed to load jobs</div>
          <p className="text-gray-600">Make sure the backend server is running</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Job Management</h1>
        <button 
          onClick={() => setShowCreateForm(true)}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center"
        >
          <span className="mr-2">➕</span>
          Create New Job
        </button>
      </div>

      {/* Jobs List */}
      <div className="bg-white rounded-lg shadow">
        {jobs && jobs.length > 0 ? (
          <div className="divide-y">
            {jobs.map((job) => (
              <JobCard key={job.id} job={job} />
            ))}
          </div>
        ) : (
          <div className="p-12 text-center text-gray-500">
            <div className="text-6xl mb-4">📋</div>
            <p className="text-xl mb-2">No jobs yet</p>
            <p className="text-sm">Create your first job posting to get started</p>
          </div>
        )}
      </div>

      {/* Create Form Modal (placeholder) */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-lg p-8 max-w-2xl w-full">
            <h2 className="text-2xl font-bold mb-4">Create New Job</h2>
            <p className="text-gray-600 mb-4">Job creation form will be implemented here</p>
            <button 
              onClick={() => setShowCreateForm(false)}
              className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function JobCard({ job }) {
  return (
    <div className="p-6 hover:bg-gray-50 transition-colors">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-800 mb-2">{job.title || 'Untitled Job'}</h3>
          <p className="text-gray-600 text-sm mb-3">{job.description || 'No description'}</p>
          <div className="flex flex-wrap gap-2">
            {job.required_skills && job.required_skills.length > 0 && (
              job.required_skills.map((skill, idx) => (
                <span key={idx} className="px-3 py-1 bg-blue-100 text-blue-700 text-xs rounded-full">
                  {skill}
                </span>
              ))
            )}
          </div>
        </div>
        <div className="ml-4">
          <span className={`px-3 py-1 rounded-full text-sm ${
            job.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
          }`}>
            {job.status || 'draft'}
          </span>
        </div>
      </div>
    </div>
  );
}

export default JobManagement;
