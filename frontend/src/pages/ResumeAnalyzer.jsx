import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, FileText, User, Mail, Phone, MapPin, Github, Linkedin, Globe,
  Briefcase, GraduationCap, Code, FolderOpen, Award, Shield, Star,
  CheckCircle, XCircle, AlertCircle, TrendingUp, Target, Loader2
} from 'lucide-react';
import toast from 'react-hot-toast';
import { Card, Button, Badge, ProgressBar } from '../components';
import api from '../api/config';

function ResumeAnalyzer() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [parsedData, setParsedData] = useState(null);
  const [qualityData, setQualityData] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setParsedData(null);
      setQualityData(null);
      toast.success(`Selected: ${acceptedFiles[0].name}`);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    multiple: false,
  });

  const analyzeResume = async () => {
    if (!file) {
      toast.error('Please select a resume file');
      return;
    }

    setUploading(true);
    setUploadStatus('Uploading resume...');
    setParsedData(null);
    setQualityData(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      // Upload and parse resume
      setUploadStatus('Uploading & parsing resume (this may take 15-30 seconds)...');
      const response = await api.post('/api/v1/resumes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000,  // 2 minute timeout for uploads
      });

      const data = response.data;
      console.log('Upload response:', data);
      
      // Fetch quality assessment
      setUploadStatus('Calculating quality score...');
      const qualityResp = await api.get(`/api/v1/resumes/${data.id}/quality?refresh=true`);
      console.log('Quality response:', qualityResp.data);
      
      // Get the parsed JSON data
      setUploadStatus('Loading parsed data...');
      const detailResp = await api.get(`/api/v1/resumes/${data.id}/parsed`);
      console.log('Parsed data:', detailResp.data);
      
      setParsedData(detailResp.data);
      setQualityData(qualityResp.data);
      setUploadStatus('');
      
      toast.success('Resume analyzed successfully!');
    } catch (error) {
      console.error('Analysis error:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to analyze resume';
      toast.error(errorMsg);
      setUploadStatus(`Error: ${errorMsg}`);
    } finally {
      setUploading(false);
    }
  };

  const getGradeColor = (grade) => {
    if (grade?.startsWith('A')) return 'text-green-600 bg-green-100';
    if (grade?.startsWith('B')) return 'text-blue-600 bg-blue-100';
    if (grade?.startsWith('C')) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'from-green-500 to-emerald-500';
    if (score >= 60) return 'from-blue-500 to-indigo-500';
    if (score >= 40) return 'from-yellow-500 to-orange-500';
    return 'from-red-500 to-pink-500';
  };

  return (
    <div className="p-8 min-h-screen animate-fade-in">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
            <Target className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gray-800">Resume Analyzer</h1>
            <p className="text-gray-600 text-lg">Upload a resume to see detailed extraction & quality score</p>
          </div>
        </div>
      </div>

      {/* Upload Section */}
      <Card className="mb-6" hover={false}>
        <div
          {...getRootProps()}
          className={`border-3 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
            isDragActive 
              ? 'border-violet-500 bg-violet-50 scale-[1.02]' 
              : 'border-gray-300 hover:border-violet-400 hover:bg-violet-50/50'
          }`}
        >
          <input {...getInputProps()} />
          <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center transition-all ${
            isDragActive ? 'bg-violet-500' : 'bg-gray-100'
          }`}>
            <Upload className={`w-8 h-8 ${isDragActive ? 'text-white' : 'text-gray-400'}`} />
          </div>
          {file ? (
            <div>
              <p className="text-lg font-semibold text-gray-800">{file.name}</p>
              <p className="text-sm text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            </div>
          ) : (
            <>
              <p className="text-lg text-gray-700 font-medium mb-1">Drop a resume here or click to browse</p>
              <p className="text-sm text-gray-400">Supports PDF, DOC, DOCX</p>
            </>
          )}
        </div>

        {file && (
          <div className="mt-4 flex flex-col items-center gap-2">
            <Button 
              onClick={analyzeResume} 
              loading={uploading}
              icon={Target}
              className="bg-gradient-to-r from-violet-500 to-purple-600"
            >
              🔍 Analyze Resume
            </Button>
            {uploadStatus && (
              <p className="text-sm text-violet-600 animate-pulse font-medium">{uploadStatus}</p>
            )}
          </div>
        )}
      </Card>

      {/* Results */}
      {parsedData && qualityData && (
        <div className="space-y-6 animate-fade-in">
          
          {/* Quality Score Card */}
          <Card hover={false} className="overflow-hidden">
            <div className="flex flex-col md:flex-row gap-6">
              {/* Score Circle */}
              <div className="flex-shrink-0 flex flex-col items-center justify-center p-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl">
                <div className={`w-32 h-32 rounded-full bg-gradient-to-br ${getScoreColor(qualityData.score)} flex items-center justify-center shadow-lg`}>
                  <div className="text-center text-white">
                    <p className="text-4xl font-bold">{Math.round(qualityData.score)}</p>
                    <p className="text-sm opacity-90">/100</p>
                  </div>
                </div>
                <div className={`mt-3 px-4 py-1 rounded-full font-bold text-lg ${getGradeColor(qualityData.grade)}`}>
                  Grade: {qualityData.grade}
                </div>
                <p className="text-sm text-gray-500 mt-1">{qualityData.tier}</p>
              </div>

              {/* Score Breakdown */}
              <div className="flex-1">
                <h3 className="font-bold text-lg mb-3 flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-violet-500" />
                  Score Breakdown
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {qualityData.breakdown && Object.entries(qualityData.breakdown).map(([key, value]) => (
                    <div key={key} className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-xs text-gray-500 capitalize">{key}</p>
                      <p className="text-lg font-bold text-gray-800">{value}</p>
                    </div>
                  ))}
                </div>
                
                {/* ATS Score */}
                <div className="mt-4 p-3 bg-blue-50 rounded-lg flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Shield className="w-5 h-5 text-blue-500" />
                    <span className="font-medium text-blue-800">ATS Compatibility</span>
                  </div>
                  <span className="font-bold text-blue-600">{qualityData.ats_score}/100</span>
                </div>
              </div>
            </div>

            {/* Strengths, Improvements, Bonuses/Penalties */}
            <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Strengths */}
              <div className="p-4 bg-green-50 rounded-xl border border-green-200">
                <h4 className="font-bold text-green-800 mb-2 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4" /> Strengths
                </h4>
                <ul className="space-y-1">
                  {qualityData.strengths?.map((s, i) => (
                    <li key={i} className="text-sm text-green-700 flex items-start gap-1">
                      <span className="text-green-500">✓</span> {s}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Improvements */}
              <div className="p-4 bg-orange-50 rounded-xl border border-orange-200">
                <h4 className="font-bold text-orange-800 mb-2 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" /> To Improve
                </h4>
                <ul className="space-y-1">
                  {qualityData.improvements?.map((s, i) => (
                    <li key={i} className="text-sm text-orange-700 flex items-start gap-1">
                      <span className="text-orange-500">→</span> {s}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Bonuses & Penalties */}
              <div className="p-4 bg-purple-50 rounded-xl border border-purple-200">
                <h4 className="font-bold text-purple-800 mb-2 flex items-center gap-2">
                  <Star className="w-4 h-4" /> Bonuses & Penalties
                </h4>
                {qualityData.bonuses?.length > 0 && (
                  <ul className="space-y-1 mb-2">
                    {qualityData.bonuses.map((b, i) => (
                      <li key={i} className="text-sm text-green-600">+ {b}</li>
                    ))}
                  </ul>
                )}
                {qualityData.penalties?.length > 0 && (
                  <ul className="space-y-1">
                    {qualityData.penalties.map((p, i) => (
                      <li key={i} className="text-sm text-red-600">- {p}</li>
                    ))}
                  </ul>
                )}
                {(!qualityData.bonuses?.length && !qualityData.penalties?.length) && (
                  <p className="text-sm text-gray-500">None detected</p>
                )}
              </div>
            </div>
          </Card>

          {/* Personal Information */}
          <Card title="👤 Personal Information" hover={false}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {parsedData.name && (
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <User className="w-5 h-5 text-violet-500" />
                  <div>
                    <p className="text-xs text-gray-500">Name</p>
                    <p className="font-semibold">{parsedData.name}</p>
                  </div>
                </div>
              )}
              {parsedData.contact_info?.emails?.[0] && (
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Mail className="w-5 h-5 text-blue-500" />
                  <div>
                    <p className="text-xs text-gray-500">Email</p>
                    <p className="font-semibold">{parsedData.contact_info.emails[0]}</p>
                  </div>
                </div>
              )}
              {parsedData.contact_info?.phones?.[0] && (
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Phone className="w-5 h-5 text-green-500" />
                  <div>
                    <p className="text-xs text-gray-500">Phone</p>
                    <p className="font-semibold">{parsedData.contact_info.phones[0]}</p>
                  </div>
                </div>
              )}
              {parsedData.contact_info?.location && (
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <MapPin className="w-5 h-5 text-red-500" />
                  <div>
                    <p className="text-xs text-gray-500">Location</p>
                    <p className="font-semibold">{parsedData.contact_info.location}</p>
                  </div>
                </div>
              )}
              {parsedData.contact_info?.github && (
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Github className="w-5 h-5 text-gray-700" />
                  <div>
                    <p className="text-xs text-gray-500">GitHub</p>
                    <a href={parsedData.contact_info.github} target="_blank" rel="noopener noreferrer" className="font-semibold text-blue-600 hover:underline">
                      {parsedData.contact_info.github.replace('https://github.com/', '')}
                    </a>
                  </div>
                </div>
              )}
              {parsedData.contact_info?.linkedin && (
                <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <Linkedin className="w-5 h-5 text-blue-700" />
                  <div>
                    <p className="text-xs text-gray-500">LinkedIn</p>
                    <a href={parsedData.contact_info.linkedin} target="_blank" rel="noopener noreferrer" className="font-semibold text-blue-600 hover:underline">
                      View Profile
                    </a>
                  </div>
                </div>
              )}
            </div>
          </Card>

          {/* Experience */}
          {parsedData.experience?.length > 0 && (
            <Card title="💼 Work Experience" hover={false}>
              <div className="space-y-4">
                {parsedData.experience.map((exp, i) => (
                  <div key={i} className="p-4 bg-gray-50 rounded-xl border-l-4 border-violet-500">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-2">
                      <div>
                        <h4 className="font-bold text-lg text-gray-800">{exp.title || 'Position'}</h4>
                        <p className="text-violet-600 font-medium">{exp.company || 'Company'}</p>
                      </div>
                      <div className="text-sm text-gray-500 mt-1 md:mt-0">
                        {exp.start_date && <span>{exp.start_date}</span>}
                        {exp.end_date && <span> - {exp.end_date}</span>}
                        {!exp.start_date && !exp.end_date && exp.duration && <span>{exp.duration}</span>}
                      </div>
                    </div>
                    {exp.description && (
                      <p className="text-sm text-gray-600 mt-2">{exp.description}</p>
                    )}
                    {exp.achievements?.length > 0 && (
                      <ul className="mt-2 space-y-1">
                        {exp.achievements.map((a, j) => (
                          <li key={j} className="text-sm text-gray-600 flex items-start gap-2">
                            <span className="text-violet-500 mt-1">•</span>
                            <span>{a}</span>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Education */}
          {parsedData.sections?.education && (
            <Card title="🎓 Education" hover={false}>
              <div className="p-4 bg-gray-50 rounded-xl">
                <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
                  {parsedData.sections.education.content}
                </pre>
              </div>
            </Card>
          )}

          {/* Projects */}
          {parsedData.sections?.projects && (
            <Card title="🚀 Projects" hover={false}>
              <div className="p-4 bg-gray-50 rounded-xl">
                <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
                  {parsedData.sections.projects.content}
                </pre>
              </div>
            </Card>
          )}

          {/* Skills */}
          {parsedData.skills?.all_skills?.length > 0 && (
            <Card title="🛠️ Skills" hover={false}>
              <div className="flex flex-wrap gap-2">
                {parsedData.skills.all_skills.map((skill, i) => (
                  <span 
                    key={i} 
                    className="px-3 py-1 bg-gradient-to-r from-violet-100 to-purple-100 text-violet-700 rounded-full text-sm font-medium border border-violet-200"
                  >
                    {skill}
                  </span>
                ))}
              </div>
              
              {/* Skills by Category */}
              {parsedData.skills.by_category && Object.keys(parsedData.skills.by_category).length > 0 && (
                <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(parsedData.skills.by_category).map(([category, skills]) => (
                    skills.length > 0 && (
                      <div key={category} className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-500 uppercase font-medium mb-2">{category}</p>
                        <div className="flex flex-wrap gap-1">
                          {skills.map((s, i) => (
                            <span key={i} className="px-2 py-0.5 bg-white rounded text-xs border">{s}</span>
                          ))}
                        </div>
                      </div>
                    )
                  ))}
                </div>
              )}
            </Card>
          )}

          {/* Certifications */}
          {parsedData.sections?.certifications && (
            <Card title="📜 Certifications" hover={false}>
              <div className="p-4 bg-gray-50 rounded-xl">
                <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
                  {parsedData.sections.certifications.content}
                </pre>
              </div>
            </Card>
          )}

          {/* Achievements */}
          {parsedData.sections?.achievements && (
            <Card title="🏆 Achievements" hover={false}>
              <div className="p-4 bg-gray-50 rounded-xl">
                <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
                  {parsedData.sections.achievements.content}
                </pre>
              </div>
            </Card>
          )}

          {/* Raw Sections (fallback) */}
          {parsedData.sections && Object.keys(parsedData.sections).filter(k => 
            !['education', 'experience', 'skills', 'projects', 'achievements', 'certifications'].includes(k)
          ).length > 0 && (
            <Card title="📋 Other Sections" hover={false}>
              <div className="space-y-3">
                {Object.entries(parsedData.sections)
                  .filter(([k]) => !['education', 'experience', 'skills', 'projects', 'achievements', 'certifications'].includes(k))
                  .map(([key, section]) => (
                    <div key={key} className="p-3 bg-gray-50 rounded-lg">
                      <p className="font-medium text-gray-700 capitalize mb-1">{key}</p>
                      <p className="text-sm text-gray-600">{section.content?.substring(0, 300)}...</p>
                    </div>
                  ))
                }
              </div>
            </Card>
          )}

        </div>
      )}
    </div>
  );
}

export default ResumeAnalyzer;
