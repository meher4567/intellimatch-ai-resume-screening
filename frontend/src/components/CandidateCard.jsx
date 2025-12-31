import React from 'react';
import { Mail, Phone, MapPin, Briefcase, GraduationCap, Award, ChevronDown, ChevronUp } from 'lucide-react';
import Badge from './Badge';

const CandidateCard = ({ 
  candidate, 
  isExpanded = false, 
  onToggleExpand,
  onSelect,
  isSelected = false 
}) => {
  const {
    name,
    email,
    phone,
    location,
    match_score = 0,
    quality_grade = 'B',
    match_details = {},
    explanation = {},
  } = candidate;

  const getTierColor = (grade) => {
    const colors = {
      'S': 'border-yellow-400',
      'A': 'border-gray-400',
      'B': 'border-orange-400',
      'C': 'border-blue-400',
      'D': 'border-green-400',
      'F': 'border-red-400',
    };
    return colors[grade] || 'border-gray-300';
  };

  return (
    <div 
      className={`
        glass-card card-hover-lift p-6 border-l-4 ${getTierColor(quality_grade)}
        transition-all duration-300 cursor-pointer relative overflow-hidden
        ${isSelected ? 'ring-2 ring-primary-500' : ''}
      `}
      onClick={() => onToggleExpand && onToggleExpand()}
    >
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-48 h-48 bg-gradient-to-br from-primary-500/10 to-secondary-500/10 rounded-full blur-3xl"></div>
      
      <div className="relative z-10">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h3 className="text-2xl font-bold text-gray-900">{name || 'Anonymous Candidate'}</h3>
              <Badge variant={`tier-${quality_grade}`} glow>
                {quality_grade} Grade
              </Badge>
            </div>
            <div className="flex flex-wrap gap-4 text-sm text-gray-600">
              {email && (
                <div className="flex items-center gap-1.5">
                  <Mail className="w-4 h-4" />
                  <span>{email}</span>
                </div>
              )}
              {phone && (
                <div className="flex items-center gap-1.5">
                  <Phone className="w-4 h-4" />
                  <span>{phone}</span>
                </div>
              )}
              {location && (
                <div className="flex items-center gap-1.5">
                  <MapPin className="w-4 h-4" />
                  <span>{location}</span>
                </div>
              )}
            </div>
          </div>
          
          {/* Match Score */}
          <div className="flex items-center gap-3">
            <div className="text-right">
              <div className="text-sm text-gray-600 font-medium mb-1">Match Score</div>
              <div className="text-4xl font-bold gradient-text">{match_score.toFixed(1)}%</div>
            </div>
            {onToggleExpand && (
              <button 
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleExpand();
                }}
              >
                {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
              </button>
            )}
          </div>
        </div>

        {/* Match Details Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="bg-white/50 backdrop-blur-sm rounded-xl p-4 text-center border border-gray-200 hover:border-primary-500 transition-colors">
            <Briefcase className="w-6 h-6 mx-auto mb-2 text-primary-500" />
            <div className="text-xs text-gray-600 uppercase tracking-wide mb-1">Skills</div>
            <div className="text-2xl font-bold gradient-text">
              {(match_details?.scores?.skills || 0).toFixed(0)}%
            </div>
          </div>
          
          <div className="bg-white/50 backdrop-blur-sm rounded-xl p-4 text-center border border-gray-200 hover:border-primary-500 transition-colors">
            <Award className="w-6 h-6 mx-auto mb-2 text-secondary-500" />
            <div className="text-xs text-gray-600 uppercase tracking-wide mb-1">Experience</div>
            <div className="text-2xl font-bold gradient-text">
              {(match_details?.scores?.experience || 0).toFixed(0)}%
            </div>
          </div>
          
          <div className="bg-white/50 backdrop-blur-sm rounded-xl p-4 text-center border border-gray-200 hover:border-primary-500 transition-colors">
            <GraduationCap className="w-6 h-6 mx-auto mb-2 text-accent-500" />
            <div className="text-xs text-gray-600 uppercase tracking-wide mb-1">Education</div>
            <div className="text-2xl font-bold gradient-text">
              {(match_details?.scores?.education || 0).toFixed(0)}%
            </div>
          </div>
          
          <div className="bg-white/50 backdrop-blur-sm rounded-xl p-4 text-center border border-gray-200 hover:border-primary-500 transition-colors">
            <Award className="w-6 h-6 mx-auto mb-2 text-primary-500" />
            <div className="text-xs text-gray-600 uppercase tracking-wide mb-1">Quality</div>
            <div className="text-2xl font-bold gradient-text">
              {(candidate.quality_score || 0).toFixed(0)}%
            </div>
          </div>
        </div>

        {/* Expanded Content */}
        {isExpanded && (
          <div className="mt-6 pt-6 border-t border-gray-200 animate-fade-in">
            <div className="bg-primary-50/50 backdrop-blur-sm rounded-xl p-4 border-l-4 border-primary-500">
              <div className="flex items-start gap-2">
                <div className="text-2xl">💡</div>
                <div className="flex-1">
                  <h4 className="font-semibold text-gray-900 mb-2">Match Explanation</h4>
                  <p className="text-gray-700 leading-relaxed">
                    {explanation?.summary || 'Strong match with relevant skills and experience.'}
                  </p>
                </div>
              </div>
            </div>

            {match_details?.matched_skills && match_details.matched_skills.length > 0 && (
              <div className="mt-4">
                <h4 className="text-sm font-semibold text-gray-700 mb-2">Matched Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {match_details.matched_skills.map((skill, idx) => (
                    <Badge key={idx} variant="primary">
                      ✓ {skill}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Selection Checkbox */}
        {onSelect && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={isSelected}
                onChange={(e) => {
                  e.stopPropagation();
                  onSelect();
                }}
                className="w-5 h-5 text-primary-600 rounded focus:ring-2 focus:ring-primary-500"
              />
              <span className="text-sm font-medium text-gray-700">
                Select for comparison
              </span>
            </label>
          </div>
        )}
      </div>
    </div>
  );
};

export default CandidateCard;
