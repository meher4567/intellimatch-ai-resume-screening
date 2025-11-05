import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/config';

function CandidateMatching() {
  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedCandidates, setSelectedCandidates] = useState([]);
  const [showComparison, setShowComparison] = useState(false);

  const { data: jobs } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      const response = await api.get('/api/v1/jobs/');
      return response.data;
    },
    retry: 2,
  });

  const { data: matches, isLoading } = useQuery({
    queryKey: ['matches', selectedJob],
    queryFn: async () => {
      if (!selectedJob) return [];
      const response = await api.post('/api/v1/matches/find', {
        job_id: selectedJob,
        top_k: 50
      });
      return response.data;
    },
    enabled: !!selectedJob,
    retry: 2,
  });

  const handleToggleSelect = (candidateId) => {
    if (selectedCandidates.includes(candidateId)) {
      setSelectedCandidates(selectedCandidates.filter(id => id !== candidateId));
    } else if (selectedCandidates.length < 3) {
      setSelectedCandidates([...selectedCandidates, candidateId]);
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Candidate Matching</h1>
        {selectedCandidates.length > 1 && (
          <button 
            onClick={() => setShowComparison(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Compare Selected ({selectedCandidates.length})
          </button>
        )}
      </div>

      {/* Job Selection */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Job
        </label>
        <select 
          className="w-full border border-gray-300 rounded-lg p-2"
          onChange={(e) => setSelectedJob(e.target.value)}
          value={selectedJob || ''}
        >
          <option value="">Choose a job...</option>
          {jobs?.map(job => (
            <option key={job.job_id} value={job.job_id}>
              {job.title} - {job.company}
            </option>
          ))}
        </select>
      </div>

      {/* Candidates List */}
      {isLoading ? (
        <div className="text-center py-8">Loading candidates...</div>
      ) : matches && matches.length > 0 ? (
        <div className="space-y-4">
          {matches.map((candidate, index) => (
            <CandidateCard
              key={candidate.resume_id}
              candidate={candidate}
              rank={index + 1}
              isSelected={selectedCandidates.includes(candidate.resume_id)}
              onToggleSelect={() => handleToggleSelect(candidate.resume_id)}
            />
          ))}
        </div>
      ) : selectedJob ? (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-600">No matching candidates found</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-600">Select a job to see matching candidates</p>
        </div>
      )}

      {/* Comparison Modal */}
      {showComparison && (
        <ComparisonModal
          candidates={matches?.filter(c => selectedCandidates.includes(c.resume_id))}
          onClose={() => setShowComparison(false)}
        />
      )}
    </div>
  );
}

function CandidateCard({ candidate, rank, isSelected, onToggleSelect }) {
  const getTierColor = (tier) => {
    const colors = {
      'S': 'text-purple-600 bg-purple-100',
      'A': 'text-green-600 bg-green-100',
      'B': 'text-blue-600 bg-blue-100',
      'C': 'text-yellow-600 bg-yellow-100',
      'D': 'text-red-600 bg-red-100'
    };
    return colors[tier] || 'text-gray-600 bg-gray-100';
  };

  return (
    <div className={`bg-white rounded-lg shadow p-6 ${isSelected ? 'ring-2 ring-blue-500' : ''}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-4 flex-1">
          <div className="text-2xl font-bold text-gray-400">#{rank}</div>
          <div className="flex-1">
            <div className="flex items-center space-x-3 mb-2">
              <h3 className="text-xl font-semibold">{candidate.name}</h3>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTierColor(candidate.tier)}`}>
                Tier {candidate.tier}
              </span>
            </div>
            <p className="text-gray-600 mb-3">{candidate.email}</p>
            
            <div className="grid grid-cols-3 gap-4 mb-3">
              <ScoreBar label="Skills" score={candidate.skills_match} />
              <ScoreBar label="Experience" score={candidate.experience_match} />
              <ScoreBar label="Education" score={candidate.education_match} />
            </div>
            
            <p className="text-sm text-gray-700">{candidate.explanation}</p>
          </div>
        </div>
        
        <div className="text-right ml-4">
          <div className="text-3xl font-bold text-blue-600 mb-2">
            {candidate.score}/100
          </div>
          <button
            onClick={onToggleSelect}
            className={`px-4 py-2 rounded-lg ${
              isSelected 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            {isSelected ? 'Selected' : 'Select'}
          </button>
        </div>
      </div>
    </div>
  );
}

function ScoreBar({ label, score }) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium">{score}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className="bg-blue-600 h-2 rounded-full" 
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}

function ComparisonModal({ candidates, onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Candidate Comparison</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>
        
        <div className="grid grid-cols-3 gap-4">
          {candidates?.map(candidate => (
            <div key={candidate.resume_id} className="border rounded-lg p-4">
              <h3 className="font-semibold text-lg mb-2">{candidate.name}</h3>
              <p className="text-sm text-gray-600 mb-3">{candidate.email}</p>
              <div className="space-y-2">
                <ComparisonRow label="Score" value={`${candidate.score}/100`} />
                <ComparisonRow label="Tier" value={candidate.tier} />
                <ComparisonRow label="Skills" value={`${candidate.skills_match}%`} />
                <ComparisonRow label="Experience" value={`${candidate.experience_match}%`} />
                <ComparisonRow label="Education" value={`${candidate.education_match}%`} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ComparisonRow({ label, value }) {
  return (
    <div className="flex justify-between text-sm">
      <span className="text-gray-600">{label}:</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

export default CandidateMatching;
