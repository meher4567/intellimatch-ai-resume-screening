import React from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/config';

function InterviewManagement() {
  const { data: interviews, isLoading } = useQuery({
    queryKey: ['interviews'],
    queryFn: async () => {
      const response = await api.get('/api/v1/interviews/');
      return response.data;
    },
    retry: 2,
  });

  if (isLoading) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <div className="text-4xl mb-4">⏳</div>
          <div className="text-xl text-gray-600">Loading interviews...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Interview Management</h1>
        <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          Schedule Interview
        </button>
      </div>
      
      <div className="bg-white rounded-lg shadow">
        {interviews && interviews.length > 0 ? (
          <div className="divide-y">
            {interviews.map((interview) => (
              <div key={interview.id} className="p-6 hover:bg-gray-50">
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-semibold text-lg">Interview #{interview.id}</h3>
                    <p className="text-gray-600 text-sm">
                      {new Date(interview.scheduled_date).toLocaleString()}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    interview.status === 'scheduled' ? 'bg-blue-100 text-blue-700' :
                    interview.status === 'completed' ? 'bg-green-100 text-green-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {interview.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-12 text-center text-gray-500">
            <div className="text-6xl mb-4">📅</div>
            <p className="text-xl mb-2">No interviews scheduled</p>
            <p className="text-sm">Schedule your first interview to get started</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default InterviewManagement;
