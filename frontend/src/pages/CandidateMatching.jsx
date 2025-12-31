import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Search, Users, TrendingUp, Award, Briefcase, GraduationCap, Calendar, Mail, Phone, MapPin, ChevronDown, ChevronUp, Sparkles, Filter, RefreshCw } from 'lucide-react';
import { Card, Button, Badge, LoadingSpinner, EmptyState, ProgressBar, Modal, StatCard } from '../components';
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
    <div className="p-8 min-h-screen animate-fade-in">
      {/* Header */}
      <div className="mb-8 animate-fade-in-down">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 gradient-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/30">
            <Users className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gray-800">Candidate Matching</h1>
            <p className="text-gray-600 text-lg">Find the best candidates with AI-powered matching ✨</p>
          </div>
        </div>
      </div>

      {/* Job Selection Card */}
      <Card className="mb-6" hover={false}>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
              Select Job Position
            </label>
            <select 
              className="input-modern"
              onChange={(e) => {
                setSelectedJob(e.target.value);
                setSelectedCandidates([]);
              }}
              value={selectedJob || ''}
            >
              <option value="">🔍 Choose a job...</option>
              {jobs?.map(job => (
                <option key={job.job_id} value={job.job_id}>
                  {job.title} - {job.company}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2 uppercase tracking-wide">
              Number of Candidates
            </label>
            <input
              type="number"
              min="5"
              max="100"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value))}
              className="input-modern"
            />
          </div>
        </div>
        
        {selectedJob && (
          <div className="mt-6 pt-6 border-t border-gray-200 flex justify-between items-center flex-wrap gap-4">
            <div className="flex items-center gap-4">
              {selectedCandidates.length > 0 && (
                <Badge variant="primary" size="lg" glow>
                  ✓ {selectedCandidates.length} selected
                </Badge>
              )}
              {matches?.length > 0 && (
                <span className="text-gray-600">
                  Found <span className="font-bold text-primary-600">{matches.length}</span> matching candidates
                </span>
              )}
            </div>
            <div className="flex gap-3">
              {selectedCandidates.length > 1 && (
                <Button 
                  variant="outline"
                  onClick={() => setShowComparison(true)}
                  icon={Filter}
                >
                  Compare ({selectedCandidates.length})
                </Button>
              )}
              <Button icon={RefreshCw} onClick={() => refetch()}>
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
        <Card hover={false}>
          <EmptyState
            icon={Users}
            title="No matching candidates found"
            description="Try adjusting the job requirements or increase the number of candidates to search."
            action={{
              label: 'Refresh Search',
              onClick: refetch
            }}
          />
        </Card>
      ) : (
        <Card hover={false}>
          <EmptyState
            icon={Search}
            title="Select a job position"
            description="Choose a job from the dropdown above to find matching candidates from your resume database."
          />
        </Card>
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
    if (score >= 85) return 'from-green-500 to-emerald-500';
    if (score >= 70) return 'from-blue-500 to-indigo-500';
    if (score >= 50) return 'from-yellow-500 to-amber-500';
    return 'from-red-500 to-rose-500';
  };

  const getRankStyle = (rank) => {
    if (rank === 1) return 'bg-gradient-to-br from-yellow-400 to-yellow-600 text-white shadow-lg shadow-yellow-500/40';
    if (rank === 2) return 'bg-gradient-to-br from-gray-300 to-gray-400 text-gray-800 shadow-lg shadow-gray-400/40';
    if (rank === 3) return 'bg-gradient-to-br from-orange-400 to-orange-600 text-white shadow-lg shadow-orange-500/40';
    return 'bg-gray-100 text-gray-600';
  };

  return (
    <Card 
      className={`transition-all duration-300 ${isSelected ? 'ring-2 ring-primary-500 shadow-glow-primary' : ''}`}
      hover={true}
    >
      <div className="flex items-start">
        {/* Rank Badge */}
        <div className="flex-shrink-0 mr-5">
          <div className={`w-14 h-14 rounded-2xl flex items-center justify-center font-bold text-xl ${getRankStyle(rank)}`}>
            #{rank}
          </div>
        </div>

        <div className="flex-1 min-w-0">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h3 className="text-2xl font-bold text-gray-900">{candidate.name}</h3>
                <Badge variant={`tier-${candidate.tier}`} glow>
                  {candidate.tier} Tier
                </Badge>
              </div>
              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600">
                {candidate.email && (
                  <span className="flex items-center gap-1.5 hover:text-primary-600 transition-colors">
                    <Mail className="w-4 h-4" />
                    {candidate.email}
                  </span>
                )}
                {candidate.phone && (
                  <span className="flex items-center gap-1.5">
                    <Phone className="w-4 h-4" />
                    {candidate.phone}
                  </span>
                )}
                {candidate.location && (
                  <span className="flex items-center gap-1.5">
                    <MapPin className="w-4 h-4" />
                    {candidate.location}
                  </span>
                )}
              </div>
            </div>

            {/* Score */}
            <div className={`px-6 py-4 rounded-2xl text-center ml-4 bg-gradient-to-br ${getScoreColor(candidate.score)} text-white shadow-lg`}>
              <div className="text-4xl font-bold">{candidate.score}</div>
              <div className="text-xs mt-1 font-medium opacity-90">Match Score</div>
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
            <div className="bg-gradient-to-r from-primary-50 to-secondary-50 rounded-xl p-4 mb-4 border-l-4 border-primary-500">
              <div className="flex items-start gap-2">
                <Sparkles className="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-gray-700 line-clamp-2 leading-relaxed">{candidate.explanation}</p>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between">
            <div className="flex gap-3">
              <Button
                variant={isSelected ? 'primary' : 'outline'}
                size="sm"
                onClick={onToggleSelect}
              >
                {isSelected ? '✓ Selected' : 'Select'}
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
            <div className="mt-6 pt-6 border-t border-gray-200 animate-fade-in">
              <MatchExplanationDetails data={candidate.explanation_data} />
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}

function ScoreBar({ label, score, icon: Icon }) {
  const getGradient = (score) => {
    if (score >= 80) return 'from-green-500 to-emerald-500';
    if (score >= 60) return 'from-blue-500 to-indigo-500';
    if (score >= 40) return 'from-yellow-500 to-amber-500';
    return 'from-red-500 to-rose-500';
  };

  return (
    <div className="bg-white/50 backdrop-blur-sm rounded-xl p-4 border border-gray-200 hover:border-primary-500 transition-all duration-200 hover:shadow-md">
      <div className="flex items-center justify-between text-sm mb-3">
        <span className="flex items-center text-gray-700 font-medium">
          {Icon && <Icon className="w-4 h-4 mr-2 text-primary-500" />}
          {label}
        </span>
        <span className="font-bold text-lg gradient-text">{score}%</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className={`h-full bg-gradient-to-r ${getGradient(score)} rounded-full transition-all duration-500`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  );
}

// New component to display detailed match explanations
function MatchExplanationDetails({ data }) {
  if (!data) return null;

  return (
    <div className="space-y-6">
      {/* Matching Skills */}
      {data.matching_skills && data.matching_skills.length > 0 && (
        <div className="animate-fade-in">
          <h4 className="font-bold text-gray-800 mb-3 flex items-center">
            <div className="w-8 h-8 rounded-lg bg-green-100 flex items-center justify-center mr-2">
              <Award className="w-4 h-4 text-green-600" />
            </div>
            Matching Skills ({data.matching_skills.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {data.matching_skills.map((skill, idx) => (
              <Badge key={idx} variant="success">✓ {skill}</Badge>
            ))}
          </div>
        </div>
      )}

      {/* Missing Skills */}
      {data.missing_skills && data.missing_skills.length > 0 && (
        <div className="animate-fade-in">
          <h4 className="font-bold text-gray-800 mb-3 flex items-center">
            <div className="w-8 h-8 rounded-lg bg-orange-100 flex items-center justify-center mr-2">
              <TrendingUp className="w-4 h-4 text-orange-600" />
            </div>
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
        <div className="animate-fade-in">
          <h4 className="font-bold text-gray-800 mb-3 flex items-center">
            <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center mr-2">
              <Calendar className="w-4 h-4 text-blue-600" />
            </div>
            Career Highlights
          </h4>
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold gradient-text">{data.career_timeline.total_years}</div>
              <div className="text-xs text-gray-600 uppercase tracking-wide">Years Experience</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold gradient-text">{data.career_timeline.total_positions}</div>
              <div className="text-xs text-gray-600 uppercase tracking-wide">Positions Held</div>
            </div>
            <div className="text-center">
              <div className={`text-2xl font-bold ${data.career_timeline.career_gaps > 0 ? 'text-orange-600' : 'text-green-600'}`}>
                {data.career_timeline.career_gaps || 0}
              </div>
              <div className="text-xs text-gray-600 uppercase tracking-wide">Career Gaps</div>
            </div>
          </div>
        </div>
      )}

      {/* Proficiency Summary */}
      {data.proficiency_summary && (
        <div className="animate-fade-in">
          <h4 className="font-bold text-gray-800 mb-3">Skill Proficiency Breakdown</h4>
          <div className="grid grid-cols-4 gap-3">
            <div className="bg-gradient-to-br from-purple-100 to-purple-50 rounded-xl p-4 text-center border border-purple-200 hover:shadow-md transition-shadow">
              <div className="text-2xl font-bold text-purple-600">{data.proficiency_summary.expert || 0}</div>
              <div className="text-xs text-gray-600 uppercase tracking-wide mt-1">Expert</div>
            </div>
            <div className="bg-gradient-to-br from-blue-100 to-blue-50 rounded-xl p-4 text-center border border-blue-200 hover:shadow-md transition-shadow">
              <div className="text-2xl font-bold text-blue-600">{data.proficiency_summary.proficient || 0}</div>
              <div className="text-xs text-gray-600 uppercase tracking-wide mt-1">Proficient</div>
            </div>
            <div className="bg-gradient-to-br from-green-100 to-green-50 rounded-xl p-4 text-center border border-green-200 hover:shadow-md transition-shadow">
              <div className="text-2xl font-bold text-green-600">{data.proficiency_summary.intermediate || 0}</div>
              <div className="text-xs text-gray-600 uppercase tracking-wide mt-1">Intermediate</div>
            </div>
            <div className="bg-gradient-to-br from-yellow-100 to-yellow-50 rounded-xl p-4 text-center border border-yellow-200 hover:shadow-md transition-shadow">
              <div className="text-2xl font-bold text-yellow-600">{data.proficiency_summary.beginner || 0}</div>
              <div className="text-xs text-gray-600 uppercase tracking-wide mt-1">Beginner</div>
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
