import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Search, Users, TrendingUp, Award, Briefcase, GraduationCap, Calendar, Mail, Phone, MapPin, ChevronDown, ChevronUp } from 'lucide-react';
import { Card, Button, Badge, LoadingSpinner, EmptyState, ProgressBar, Modal } from '../components';
import api from '../api/config';

function CandidateMatching() {
  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedCandidates, setSelectedCandidates] = useState([]);
  const [showComparison, setShowComparison] = useState(false);
  const [expandedCandidate, setExpandedCandidate] = useState(null);
  const [topK, setTopK] = useState(20);

  const { data: jobs } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      const response = await api.get('/api/v1/jobs/');
      return response.data;
    },
    retry: 2,
  });

  const { data: matches, isLoading, refetch } = useQuery({
    queryKey: ['matches', selectedJob, topK],
    queryFn: async () => {
      if (!selectedJob) return [];
      const loadingToast = toast.loading('Finding matching candidates...');
      try {
        const response = await api.post('/api/v1/matches/find', {
          job_id: selectedJob,
          top_k: topK,
          include_explanation: true
        });
        toast.success(`Found ${response.data.length} matching candidates!`, { id: loadingToast });
        return response.data;
      } catch (error) {
        toast.error('Failed to find matches', { id: loadingToast });
        throw error;
      }
    },
    enabled: !!selectedJob,
    retry: 1,
  });

  const handleToggleSelect = (candidateId) => {
    if (selectedCandidates.includes(candidateId)) {
      setSelectedCandidates(selectedCandidates.filter(id => id !== candidateId));
    } else if (selectedCandidates.length < 3) {
      setSelectedCandidates([...selectedCandidates, candidateId]);
    }
  };

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Candidate Matching</h1>
        <p className="text-gray-600 mt-2">Find the best candidates for your job openings with AI-powered matching</p>
      </div>

      {/* Job Selection Card */}
      <Card className="mb-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Job Position
            </label>
            <select 
              className="w-full border-2 border-gray-300 rounded-lg p-3 text-base focus:border-blue-500 focus:outline-none transition-colors"
              onChange={(e) => {
                setSelectedJob(e.target.value);
                setSelectedCandidates([]);
              }}
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
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Candidates
            </label>
            <input
              type="number"
              min="5"
              max="100"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value))}
              className="w-full border-2 border-gray-300 rounded-lg p-3 text-base focus:border-blue-500 focus:outline-none transition-colors"
            />
          </div>
        </div>
        
        {selectedJob && (
          <div className="mt-4 flex justify-between items-center">
            <div className="flex items-center space-x-4">
              {selectedCandidates.length > 0 && (
                <Badge variant="primary" size="lg">
                  {selectedCandidates.length} selected
                </Badge>
              )}
            </div>
            <div className="flex space-x-3">
              {selectedCandidates.length > 1 && (
                <Button 
                  variant="outline"
                  onClick={() => setShowComparison(true)}
                >
                  Compare ({selectedCandidates.length})
                </Button>
              )}
              <Button icon={Search} onClick={() => refetch()}>
                Refresh Matches
              </Button>
            </div>
          </div>
        )}
      </Card>

      {/* Candidates List */}
      {isLoading ? (
        <LoadingSpinner size="lg" text="Finding best matching candidates..." />
      ) : matches && matches.length > 0 ? (
        <div className="space-y-4">
          {matches.map((candidate, index) => (
            <CandidateCard
              key={candidate.resume_id}
              candidate={candidate}
              rank={index + 1}
              isSelected={selectedCandidates.includes(candidate.resume_id)}
              onToggleSelect={() => handleToggleSelect(candidate.resume_id)}
              isExpanded={expandedCandidate === candidate.resume_id}
              onToggleExpand={() => setExpandedCandidate(
                expandedCandidate === candidate.resume_id ? null : candidate.resume_id
              )}
            />
          ))}
        </div>
      ) : selectedJob ? (
        <EmptyState
          icon={Users}
          title="No matching candidates found"
          description="Try adjusting the job requirements or increase the number of candidates to search."
          action={{
            label: 'Refresh Search',
            onClick: refetch
          }}
        />
      ) : (
        <EmptyState
          icon={Search}
          title="Select a job position"
          description="Choose a job from the dropdown above to find matching candidates from your resume database."
        />
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

function CandidateCard({ candidate, rank, isSelected, onToggleSelect, isExpanded, onToggleExpand }) {
  const getScoreColor = (score) => {
    if (score >= 85) return 'text-green-600 bg-green-50';
    if (score >= 70) return 'text-blue-600 bg-blue-50';
    if (score >= 50) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <Card className={`hover:shadow-xl transition-all ${isSelected ? 'ring-2 ring-blue-500 shadow-lg' : ''}`}>
      <div className="flex items-start">
        {/* Rank Badge */}
        <div className="flex-shrink-0 mr-4">
          <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg ${
            rank <= 3 ? 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-white' : 'bg-gray-100 text-gray-600'
          }`}>
            #{rank}
          </div>
        </div>

        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-start justify-between mb-3">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <h3 className="text-xl font-bold text-gray-900">{candidate.name}</h3>
                <Badge variant={`tier-${candidate.tier}`}>
                  Tier {candidate.tier}
                </Badge>
              </div>
              <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600">
                {candidate.email && (
                  <span className="flex items-center">
                    <Mail className="w-4 h-4 mr-1" />
                    {candidate.email}
                  </span>
                )}
                {candidate.phone && (
                  <span className="flex items-center">
                    <Phone className="w-4 h-4 mr-1" />
                    {candidate.phone}
                  </span>
                )}
                {candidate.location && (
                  <span className="flex items-center">
                    <MapPin className="w-4 h-4 mr-1" />
                    {candidate.location}
                  </span>
                )}
              </div>
            </div>

            {/* Score */}
            <div className={`px-6 py-3 rounded-xl text-center ml-4 ${getScoreColor(candidate.score)}`}>
              <div className="text-3xl font-bold">{candidate.score}</div>
              <div className="text-xs mt-1 font-medium">Match Score</div>
            </div>
          </div>

          {/* Score Breakdown */}
          <div className="grid grid-cols-3 gap-4 mb-4">
            <ScoreBar 
              label="Skills" 
              score={candidate.skills_match || candidate.score} 
              icon={Award}
            />
            <ScoreBar 
              label="Experience" 
              score={candidate.experience_match || Math.round(candidate.score * 0.9)} 
              icon={Briefcase}
            />
            <ScoreBar 
              label="Education" 
              score={candidate.education_match || Math.round(candidate.score * 0.85)} 
              icon={GraduationCap}
            />
          </div>

          {/* Explanation Preview */}
          {candidate.explanation && (
            <div className="bg-gray-50 rounded-lg p-3 mb-3">
              <p className="text-sm text-gray-700 line-clamp-2">{candidate.explanation}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between">
            <div className="flex space-x-2">
              <Button
                variant={isSelected ? 'primary' : 'outline'}
                size="sm"
                onClick={onToggleSelect}
              >
                {isSelected ? 'Selected ✓' : 'Select'}
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={onToggleExpand}
                icon={isExpanded ? ChevronUp : ChevronDown}
              >
                {isExpanded ? 'Less' : 'More'} Details
              </Button>
            </div>
          </div>

          {/* Expanded Details */}
          {isExpanded && candidate.explanation_data && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <MatchExplanationDetails data={candidate.explanation_data} />
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}

function ScoreBar({ label, score, icon: Icon }) {
  const getColor = (score) => {
    if (score >= 80) return 'green';
    if (score >= 60) return 'blue';
    if (score >= 40) return 'yellow';
    return 'red';
  };

  return (
    <div>
      <div className="flex items-center justify-between text-sm mb-2">
        <span className="flex items-center text-gray-700">
          {Icon && <Icon className="w-4 h-4 mr-1" />}
          {label}
        </span>
        <span className="font-semibold text-gray-900">{score}%</span>
      </div>
      <ProgressBar value={score} color={getColor(score)} showPercentage={false} />
    </div>
  );
}

// New component to display detailed match explanations
function MatchExplanationDetails({ data }) {
  if (!data) return null;

  return (
    <div className="space-y-4">
      {/* Matching Skills */}
      {data.matching_skills && data.matching_skills.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-2 flex items-center">
            <Award className="w-4 h-4 mr-2 text-green-600" />
            Matching Skills ({data.matching_skills.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {data.matching_skills.map((skill, idx) => (
              <Badge key={idx} variant="success">{skill}</Badge>
            ))}
          </div>
        </div>
      )}

      {/* Missing Skills */}
      {data.missing_skills && data.missing_skills.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-2 flex items-center">
            <TrendingUp className="w-4 h-4 mr-2 text-orange-600" />
            Skills to Develop ({data.missing_skills.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {data.missing_skills.map((skill, idx) => (
              <Badge key={idx} variant="warning">{skill}</Badge>
            ))}
          </div>
        </div>
      )}

      {/* Career Timeline */}
      {data.career_timeline && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-2 flex items-center">
            <Calendar className="w-4 h-4 mr-2 text-blue-600" />
            Career Highlights
          </h4>
          <div className="bg-blue-50 rounded-lg p-3 space-y-2">
            <p className="text-sm"><strong>Total Experience:</strong> {data.career_timeline.total_years} years</p>
            <p className="text-sm"><strong>Positions:</strong> {data.career_timeline.total_positions}</p>
            {data.career_timeline.career_gaps > 0 && (
              <p className="text-sm text-orange-600"><strong>Career Gaps:</strong> {data.career_timeline.career_gaps} detected</p>
            )}
          </div>
        </div>
      )}

      {/* Proficiency Summary */}
      {data.proficiency_summary && (
        <div>
          <h4 className="font-semibold text-gray-800 mb-2">Skill Proficiency Breakdown</h4>
          <div className="grid grid-cols-4 gap-2">
            <div className="bg-purple-50 rounded p-2 text-center">
              <div className="text-lg font-bold text-purple-600">{data.proficiency_summary.expert || 0}</div>
              <div className="text-xs text-gray-600">Expert</div>
            </div>
            <div className="bg-blue-50 rounded p-2 text-center">
              <div className="text-lg font-bold text-blue-600">{data.proficiency_summary.proficient || 0}</div>
              <div className="text-xs text-gray-600">Proficient</div>
            </div>
            <div className="bg-green-50 rounded p-2 text-center">
              <div className="text-lg font-bold text-green-600">{data.proficiency_summary.intermediate || 0}</div>
              <div className="text-xs text-gray-600">Intermediate</div>
            </div>
            <div className="bg-yellow-50 rounded p-2 text-center">
              <div className="text-lg font-bold text-yellow-600">{data.proficiency_summary.beginner || 0}</div>
              <div className="text-xs text-gray-600">Beginner</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ComparisonModal({ candidates, onClose }) {
  if (!candidates || candidates.length === 0) return null;

  const metrics = [
    { key: 'score', label: 'Overall Match', format: (v) => `${v}/100` },
    { key: 'skills_match', label: 'Skills Match', format: (v) => `${v}%` },
    { key: 'experience_match', label: 'Experience', format: (v) => `${v}%` },
    { key: 'education_match', label: 'Education', format: (v) => `${v}%` },
  ];

  return (
    <Modal
      isOpen={true}
      onClose={onClose}
      title={`Compare ${candidates.length} Candidates`}
      size="xl"
    >
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-gray-200">
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Metric</th>
              {candidates.map(candidate => (
                <th key={candidate.resume_id} className="text-center py-3 px-4">
                  <div>
                    <div className="font-bold text-gray-900">{candidate.name}</div>
                    <Badge variant={`tier-${candidate.tier}`} className="mt-1">
                      Tier {candidate.tier}
                    </Badge>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {metrics.map((metric, idx) => (
              <tr key={metric.key} className={idx % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
                <td className="py-3 px-4 font-medium text-gray-700">{metric.label}</td>
                {candidates.map(candidate => {
                  const value = candidate[metric.key] || 0;
                  const formatted = metric.format(value);
                  const isHighest = value === Math.max(...candidates.map(c => c[metric.key] || 0));
                  
                  return (
                    <td key={candidate.resume_id} className="text-center py-3 px-4">
                      <span className={`font-bold ${isHighest ? 'text-green-600' : 'text-gray-600'}`}>
                        {formatted}
                        {isHighest && ' 🏆'}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        {candidates.map(candidate => (
          <Card key={candidate.resume_id}>
            <h4 className="font-semibold mb-2">{candidate.name}</h4>
            {candidate.explanation && (
              <p className="text-sm text-gray-600">{candidate.explanation}</p>
            )}
          </Card>
        ))}
      </div>
    </Modal>
  );
}

export default CandidateMatching;
