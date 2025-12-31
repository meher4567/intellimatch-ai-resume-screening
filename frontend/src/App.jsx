import React, { useState } from 'react';
import api from './api/config';

// Professional CSS-in-JS styles - Modern Design System
const colors = {
  primary: '#6366f1',
  primaryDark: '#4f46e5',
  success: '#10b981',
  successLight: '#d1fae5',
  warning: '#f59e0b',
  warningLight: '#fef3c7',
  danger: '#ef4444',
  dangerLight: '#fee2e2',
  gray: { 50: '#f9fafb', 100: '#f3f4f6', 200: '#e5e7eb', 300: '#d1d5db', 400: '#9ca3af', 500: '#6b7280', 600: '#4b5563', 700: '#374151', 800: '#1f2937', 900: '#111827' },
};

const getGradient = (score) => {
  if (score >= 80) return 'linear-gradient(135deg, #10b981 0%, #34d399 100%)';
  if (score >= 60) return 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)';
  if (score >= 40) return 'linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)';
  return 'linear-gradient(135deg, #ef4444 0%, #f87171 100%)';
};

const getGradeInfo = (grade) => {
  const grades = {
    'A+': { label: 'Exceptional', color: '#059669', bg: '#d1fae5' },
    'A': { label: 'Excellent', color: '#10b981', bg: '#d1fae5' },
    'B+': { label: 'Very Good', color: '#6366f1', bg: '#e0e7ff' },
    'B': { label: 'Good', color: '#6366f1', bg: '#e0e7ff' },
    'C+': { label: 'Above Average', color: '#f59e0b', bg: '#fef3c7' },
    'C': { label: 'Average', color: '#f59e0b', bg: '#fef3c7' },
    'D': { label: 'Needs Work', color: '#ef4444', bg: '#fee2e2' },
    'F': { label: 'Poor', color: '#dc2626', bg: '#fee2e2' },
  };
  return grades[grade] || grades['C'];
};

// Skill categories with icons
const skillCategories = {
  'Programming': ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r'],
  'Frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'node', 'express', 'fastapi', 'rails', 'laravel', 'nextjs', 'nuxt'],
  'Cloud & DevOps': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 'ansible', 'ci/cd', 'linux', 'git'],
  'Data & AI': ['sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'nlp', 'data science'],
};

const categorizeSkills = (skills) => {
  const categorized = { 'Programming': [], 'Frameworks': [], 'Cloud & DevOps': [], 'Data & AI': [], 'Other': [] };
  skills.forEach(skill => {
    const lowerSkill = skill.toLowerCase();
    let found = false;
    for (const [category, keywords] of Object.entries(skillCategories)) {
      if (keywords.some(k => lowerSkill.includes(k))) {
        categorized[category].push(skill);
        found = true;
        break;
      }
    }
    if (!found) categorized['Other'].push(skill);
  });
  return categorized;
};

function App() {
  const [activeTab, setActiveTab] = useState('analyzer');
  
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 50%, #334155 100%)',
      fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    }}>
      {/* Animated Background Blobs */}
      <div style={{
        position: 'fixed', top: '-20%', left: '-10%', width: '500px', height: '500px',
        background: 'radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%)',
        borderRadius: '50%', filter: 'blur(60px)', pointerEvents: 'none',
      }} />
      <div style={{
        position: 'fixed', bottom: '-20%', right: '-10%', width: '600px', height: '600px',
        background: 'radial-gradient(circle, rgba(139,92,246,0.1) 0%, transparent 70%)',
        borderRadius: '50%', filter: 'blur(80px)', pointerEvents: 'none',
      }} />

      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '40px 24px', position: 'relative', zIndex: 1 }}>
        {/* Header */}
        <header style={{ textAlign: 'center', marginBottom: '48px' }}>
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <div style={{
              width: '56px', height: '56px', borderRadius: '16px',
              background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 20px 40px rgba(99,102,241,0.4)',
            }}>
              <span style={{ fontSize: '28px' }}>✨</span>
            </div>
            <h1 style={{
              fontSize: '42px', fontWeight: '800', margin: 0,
              background: 'linear-gradient(135deg, #fff 0%, #a5b4fc 100%)',
              WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
              letterSpacing: '-0.02em',
            }}>
              IntelliMatch
            </h1>
          </div>
          <p style={{ color: '#94a3b8', fontSize: '18px', margin: 0, fontWeight: '500' }}>
            AI-Powered Resume Analysis & Intelligent Candidate Matching
          </p>
        </header>

        {/* Tab Navigation */}
        <nav style={{
          display: 'flex', justifyContent: 'center', gap: '8px', marginBottom: '32px',
          background: 'rgba(30,41,59,0.8)', padding: '8px', borderRadius: '16px',
          backdropFilter: 'blur(20px)', width: 'fit-content', margin: '0 auto 32px',
          border: '1px solid rgba(148,163,184,0.1)',
        }}>
          {[
            { id: 'analyzer', icon: '📊', label: 'Resume Analyzer' },
            { id: 'manager', icon: '👥', label: 'Resume Manager' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: '14px 32px', fontSize: '15px', fontWeight: '600', border: 'none',
                borderRadius: '12px', cursor: 'pointer', transition: 'all 0.3s ease',
                background: activeTab === tab.id ? 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' : 'transparent',
                color: activeTab === tab.id ? 'white' : '#94a3b8',
                boxShadow: activeTab === tab.id ? '0 10px 30px rgba(99,102,241,0.3)' : 'none',
              }}
            >
              <span style={{ marginRight: '8px' }}>{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Main Content Card */}
        <main style={{
          background: 'rgba(30,41,59,0.6)', borderRadius: '24px', padding: '40px',
          backdropFilter: 'blur(20px)', border: '1px solid rgba(148,163,184,0.1)',
          boxShadow: '0 25px 50px rgba(0,0,0,0.25)',
        }}>
          {activeTab === 'analyzer' ? <ResumeAnalyzer /> : <ResumeManager />}
        </main>
      </div>
    </div>
  );
}

// ============ RESUME ANALYZER ============
function ResumeAnalyzer() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [quality, setQuality] = useState(null);
  const [parsed, setParsed] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const handleUpload = async () => {
    if (!file) return alert('Please select a file');
    
    setUploading(true);
    setResult(null);
    setQuality(null);
    setParsed(null);

    try {
      const formData = new FormData();
      formData.append('files', file);
      
      const uploadRes = await api.post('/api/v1/resumes/batch-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      console.log('Upload response:', uploadRes.data);
      setResult(uploadRes.data);

      if (uploadRes.data.successful?.length > 0) {
        const resumeId = uploadRes.data.successful[0].resume_id;
        
        const [qualityRes, parsedRes] = await Promise.all([
          api.get(`/api/v1/resumes/${resumeId}/quality`),
          api.get(`/api/v1/resumes/${resumeId}/parsed`)
        ]);
        
        console.log('Quality:', qualityRes.data);
        console.log('Parsed:', parsedRes.data);
        
        setQuality(qualityRes.data);
        setParsed(parsedRes.data);
      }
    } catch (err) {
      console.error('Error:', err);
      alert('Error: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  const gradeInfo = quality ? getGradeInfo(quality.grade) : null;
  const categorizedSkills = parsed?.skills?.all_skills ? categorizeSkills(parsed.skills.all_skills) : null;

  return (
    <div>
      {/* Section Header */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#f1f5f9', margin: '0 0 8px 0' }}>
          Resume Analyzer
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '16px', margin: 0 }}>
          Get instant AI-powered feedback on your resume with detailed scoring and improvement tips
        </p>
      </div>

      {/* Upload Area */}
      <label
        style={{
          display: 'block', padding: '48px 32px', textAlign: 'center', cursor: 'pointer',
          border: `2px dashed ${dragOver ? '#6366f1' : '#475569'}`, borderRadius: '16px',
          background: dragOver ? 'rgba(99,102,241,0.1)' : 'rgba(51,65,85,0.5)',
          transition: 'all 0.3s ease', marginBottom: '24px',
        }}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); setFile(e.dataTransfer.files[0]); }}
      >
        <input type="file" accept=".pdf,.doc,.docx" style={{ display: 'none' }} onChange={(e) => setFile(e.target.files[0])} />
        <div style={{
          width: '80px', height: '80px', borderRadius: '20px', margin: '0 auto 20px',
          background: file ? 'linear-gradient(135deg, #10b981 0%, #34d399 100%)' : 'linear-gradient(135deg, #475569 0%, #64748b 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '36px',
        }}>
          {file ? '✓' : '📄'}
        </div>
        <div style={{ fontSize: '18px', fontWeight: '600', color: '#e2e8f0', marginBottom: '8px' }}>
          {file ? file.name : 'Drop your resume here or click to browse'}
        </div>
        <div style={{ fontSize: '14px', color: '#64748b' }}>
          Supports PDF, DOC, DOCX • Max 5MB
        </div>
      </label>

      {/* Upload Button */}
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <button
          onClick={handleUpload}
          disabled={uploading || !file}
          style={{
            padding: '16px 48px', fontSize: '16px', fontWeight: '600', border: 'none',
            borderRadius: '12px', cursor: uploading || !file ? 'not-allowed' : 'pointer',
            background: uploading || !file ? '#475569' : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
            color: 'white', transition: 'all 0.3s ease',
            boxShadow: uploading || !file ? 'none' : '0 10px 30px rgba(99,102,241,0.4)',
            opacity: uploading || !file ? 0.6 : 1,
          }}
        >
          {uploading ? (
            <span>⏳ Analyzing Resume...</span>
          ) : (
            <span>🚀 Analyze Resume</span>
          )}
        </button>
      </div>

      {/* Results Section */}
      {quality && parsed && (
        <div style={{ animation: 'fadeIn 0.5s ease' }}>
          {/* Score Hero Section */}
          <div style={{
            background: 'linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(139,92,246,0.2) 100%)',
            borderRadius: '20px', padding: '40px', marginBottom: '32px',
            border: '1px solid rgba(99,102,241,0.3)', textAlign: 'center',
          }}>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '48px', flexWrap: 'wrap' }}>
              {/* Score Circle */}
              <div style={{ position: 'relative' }}>
                <svg width="180" height="180" viewBox="0 0 180 180">
                  <circle cx="90" cy="90" r="80" fill="none" stroke="#334155" strokeWidth="12" />
                  <circle
                    cx="90" cy="90" r="80" fill="none"
                    stroke={quality.score >= 70 ? '#10b981' : quality.score >= 50 ? '#6366f1' : '#f59e0b'}
                    strokeWidth="12" strokeLinecap="round"
                    strokeDasharray={`${(quality.score / 100) * 502} 502`}
                    transform="rotate(-90 90 90)"
                    style={{ transition: 'stroke-dasharray 1s ease' }}
                  />
                </svg>
                <div style={{
                  position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
                  textAlign: 'center',
                }}>
                  <div style={{ fontSize: '48px', fontWeight: '800', color: '#f1f5f9' }}>{Math.round(quality.score)}</div>
                  <div style={{ fontSize: '14px', color: '#94a3b8', fontWeight: '500' }}>out of 100</div>
                </div>
              </div>

              {/* Grade & Quick Stats */}
              <div style={{ textAlign: 'left' }}>
                <div style={{
                  display: 'inline-block', padding: '12px 24px', borderRadius: '12px',
                  background: gradeInfo.bg, marginBottom: '16px',
                }}>
                  <span style={{ fontSize: '32px', fontWeight: '800', color: gradeInfo.color }}>{quality.grade}</span>
                  <span style={{ fontSize: '16px', color: gradeInfo.color, marginLeft: '12px' }}>{gradeInfo.label}</span>
                </div>
                <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap' }}>
                  <div>
                    <div style={{ fontSize: '24px', fontWeight: '700', color: '#f1f5f9' }}>
                      {parsed.skills?.all_skills?.length || 0}
                    </div>
                    <div style={{ fontSize: '13px', color: '#64748b' }}>Skills Found</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '24px', fontWeight: '700', color: '#f1f5f9' }}>
                      {parsed.experience?.length || 0}
                    </div>
                    <div style={{ fontSize: '13px', color: '#64748b' }}>Positions</div>
                  </div>
                  <div>
                    <div style={{ fontSize: '24px', fontWeight: '700', color: '#f1f5f9' }}>
                      {parsed.projects?.length || 0}
                    </div>
                    <div style={{ fontSize: '13px', color: '#64748b' }}>Projects</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Contact Card */}
          {parsed.contact_info && (
            <div style={{
              background: 'rgba(51,65,85,0.5)', borderRadius: '16px', padding: '24px',
              marginBottom: '24px', border: '1px solid rgba(71,85,105,0.5)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
                <div style={{
                  width: '56px', height: '56px', borderRadius: '16px',
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '24px', fontWeight: '700', color: 'white',
                }}>
                  {(parsed.name || 'U')[0].toUpperCase()}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '20px', fontWeight: '700', color: '#f1f5f9' }}>{parsed.name || 'Candidate'}</div>
                  <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginTop: '4px' }}>
                    {parsed.contact_info.emails?.[0] && (
                      <span style={{ color: '#94a3b8', fontSize: '14px' }}>📧 {parsed.contact_info.emails[0]}</span>
                    )}
                    {parsed.contact_info.phones?.[0] && (
                      <span style={{ color: '#94a3b8', fontSize: '14px' }}>📞 {parsed.contact_info.phones[0]}</span>
                    )}
                    {parsed.contact_info.linkedin && (
                      <span style={{ color: '#94a3b8', fontSize: '14px' }}>🔗 LinkedIn</span>
                    )}
                    {parsed.contact_info.github && (
                      <span style={{ color: '#94a3b8', fontSize: '14px' }}>💻 GitHub</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Pros & Cons Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px', marginBottom: '24px' }}>
            {/* Strengths (Pros) */}
            <div style={{
              background: 'rgba(16,185,129,0.1)', borderRadius: '16px', padding: '24px',
              border: '1px solid rgba(16,185,129,0.3)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <div style={{
                  width: '40px', height: '40px', borderRadius: '10px', background: '#10b981',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px',
                }}>✓</div>
                <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#10b981' }}>Strengths</h3>
              </div>
              {quality.strengths?.slice(0, 5).map((s, i) => (
                <div key={i} style={{
                  padding: '12px 16px', marginBottom: '10px', borderRadius: '10px',
                  background: 'rgba(16,185,129,0.15)', color: '#34d399', fontSize: '14px',
                  borderLeft: '3px solid #10b981',
                }}>
                  {s}
                </div>
              ))}
            </div>

            {/* Improvements (Cons) */}
            <div style={{
              background: 'rgba(245,158,11,0.1)', borderRadius: '16px', padding: '24px',
              border: '1px solid rgba(245,158,11,0.3)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <div style={{
                  width: '40px', height: '40px', borderRadius: '10px', background: '#f59e0b',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px',
                }}>💡</div>
                <h3 style={{ margin: 0, fontSize: '18px', fontWeight: '700', color: '#f59e0b' }}>Areas to Improve</h3>
              </div>
              {quality.improvements?.slice(0, 5).map((s, i) => (
                <div key={i} style={{
                  padding: '12px 16px', marginBottom: '10px', borderRadius: '10px',
                  background: 'rgba(245,158,11,0.15)', color: '#fbbf24', fontSize: '14px',
                  borderLeft: '3px solid #f59e0b',
                }}>
                  {s}
                </div>
              ))}
            </div>
          </div>

          {/* Skills by Category */}
          {categorizedSkills && (
            <div style={{
              background: 'rgba(51,65,85,0.5)', borderRadius: '16px', padding: '24px',
              marginBottom: '24px', border: '1px solid rgba(71,85,105,0.5)',
            }}>
              <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '700', color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px' }}>🛠️</span> Skills Overview
                <span style={{ fontSize: '14px', color: '#64748b', fontWeight: '500' }}>
                  ({parsed.skills.all_skills.length} total)
                </span>
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
                {Object.entries(categorizedSkills).filter(([_, skills]) => skills.length > 0).slice(0, 4).map(([category, skills]) => (
                  <div key={category}>
                    <div style={{ fontSize: '13px', fontWeight: '600', color: '#94a3b8', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      {category} ({skills.length})
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {skills.slice(0, 6).map((skill, i) => (
                        <span key={i} style={{
                          padding: '6px 14px', borderRadius: '20px', fontSize: '13px', fontWeight: '500',
                          background: category === 'Programming' ? 'rgba(99,102,241,0.2)' :
                                     category === 'Frameworks' ? 'rgba(139,92,246,0.2)' :
                                     category === 'Cloud & DevOps' ? 'rgba(16,185,129,0.2)' :
                                     category === 'Data & AI' ? 'rgba(245,158,11,0.2)' : 'rgba(100,116,139,0.2)',
                          color: category === 'Programming' ? '#a5b4fc' :
                                 category === 'Frameworks' ? '#c4b5fd' :
                                 category === 'Cloud & DevOps' ? '#6ee7b7' :
                                 category === 'Data & AI' ? '#fcd34d' : '#cbd5e1',
                        }}>
                          {skill}
                        </span>
                      ))}
                      {skills.length > 6 && (
                        <span style={{ padding: '6px 12px', color: '#64748b', fontSize: '12px' }}>
                          +{skills.length - 6} more
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Experience Highlights */}
          {parsed.experience?.length > 0 && (
            <div style={{
              background: 'rgba(51,65,85,0.5)', borderRadius: '16px', padding: '24px',
              marginBottom: '24px', border: '1px solid rgba(71,85,105,0.5)',
            }}>
              <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '700', color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px' }}>💼</span> Experience Highlights
              </h3>
              {parsed.experience.slice(0, 3).map((exp, i) => (
                <div key={i} style={{
                  padding: '20px', marginBottom: '16px', borderRadius: '12px',
                  background: 'rgba(30,41,59,0.8)', borderLeft: '4px solid #6366f1',
                }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
                    <div>
                      <div style={{ fontSize: '16px', fontWeight: '700', color: '#f1f5f9' }}>{exp.title || 'Position'}</div>
                      <div style={{ fontSize: '14px', color: '#a5b4fc' }}>{exp.company || 'Company'}</div>
                    </div>
                    {exp.dates && (
                      <span style={{
                        padding: '4px 12px', borderRadius: '6px', fontSize: '12px',
                        background: 'rgba(99,102,241,0.2)', color: '#a5b4fc',
                      }}>
                        {exp.dates}
                      </span>
                    )}
                  </div>
                  {exp.achievements?.slice(0, 2).map((a, j) => (
                    <div key={j} style={{ fontSize: '14px', color: '#94a3b8', marginTop: '8px', paddingLeft: '16px', borderLeft: '2px solid #475569' }}>
                      {a}
                    </div>
                  ))}
                </div>
              ))}
              {parsed.experience.length > 3 && (
                <div style={{ textAlign: 'center', color: '#64748b', fontSize: '14px' }}>
                  +{parsed.experience.length - 3} more positions
                </div>
              )}
            </div>
          )}

          {/* Projects Highlights */}
          {parsed.projects?.length > 0 && (
            <div style={{
              background: 'rgba(51,65,85,0.5)', borderRadius: '16px', padding: '24px',
              marginBottom: '24px', border: '1px solid rgba(71,85,105,0.5)',
            }}>
              <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '700', color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px' }}>🚀</span> Project Highlights
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
                {parsed.projects.slice(0, 4).map((proj, i) => (
                  <div key={i} style={{
                    padding: '20px', borderRadius: '12px', background: 'rgba(30,41,59,0.8)',
                    border: '1px solid rgba(71,85,105,0.5)',
                  }}>
                    <div style={{ fontSize: '15px', fontWeight: '700', color: '#f1f5f9', marginBottom: '8px' }}>
                      {proj.name || proj.title || `Project ${i + 1}`}
                    </div>
                    {proj.description && (
                      <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '12px', lineHeight: '1.5' }}>
                        {proj.description.substring(0, 120)}{proj.description.length > 120 ? '...' : ''}
                      </div>
                    )}
                    {proj.technologies?.length > 0 && (
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                        {proj.technologies.slice(0, 4).map((tech, j) => (
                          <span key={j} style={{
                            padding: '4px 10px', borderRadius: '6px', fontSize: '11px',
                            background: 'rgba(139,92,246,0.2)', color: '#c4b5fd',
                          }}>
                            {tech}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Education */}
          {(parsed.education?.length > 0 || parsed.sections?.education?.content) && (
            <div style={{
              background: 'rgba(51,65,85,0.5)', borderRadius: '16px', padding: '24px',
              border: '1px solid rgba(71,85,105,0.5)',
            }}>
              <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '700', color: '#f1f5f9', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{ fontSize: '24px' }}>🎓</span> Education
              </h3>
              {parsed.education?.length > 0 ? (
                parsed.education.slice(0, 2).map((edu, i) => (
                  <div key={i} style={{
                    padding: '16px', marginBottom: '12px', borderRadius: '10px',
                    background: 'rgba(30,41,59,0.8)',
                  }}>
                    <div style={{ fontSize: '15px', fontWeight: '600', color: '#f1f5f9' }}>{edu.degree || edu.field}</div>
                    <div style={{ fontSize: '14px', color: '#a5b4fc' }}>{edu.institution || edu.school}</div>
                    {edu.year && <div style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>{edu.year}</div>}
                  </div>
                ))
              ) : (
                <div style={{ fontSize: '14px', color: '#94a3b8', lineHeight: '1.6' }}>
                  {parsed.sections?.education?.content?.substring(0, 300)}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ============ RESUME MANAGER ============
function ResumeManager() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [resumes, setResumes] = useState([]);
  const [skillFilter, setSkillFilter] = useState('');
  const [minScore, setMinScore] = useState(0);
  const [selectedResume, setSelectedResume] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFilesChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleBulkUpload = async () => {
    if (files.length === 0) return alert('Please select files');
    
    setUploading(true);
    
    try {
      const formData = new FormData();
      files.forEach(f => formData.append('files', f));
      
      const uploadRes = await api.post('/api/v1/resumes/batch-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      
      console.log('Bulk upload:', uploadRes.data);

      // Fetch details for each uploaded resume
      const resumeData = await Promise.all(
        uploadRes.data.successful.map(async (item) => {
          try {
            const [qualityRes, parsedRes] = await Promise.all([
              api.get(`/api/v1/resumes/${item.resume_id}/quality`),
              api.get(`/api/v1/resumes/${item.resume_id}/parsed`)
            ]);
            return {
              id: item.resume_id,
              filename: item.filename,
              name: item.name || parsedRes.data.name || 'Unknown',
              score: qualityRes.data.score,
              grade: qualityRes.data.grade,
              strengths: qualityRes.data.strengths || [],
              improvements: qualityRes.data.improvements || [],
              skills: parsedRes.data.skills?.all_skills || [],
              experience: parsedRes.data.experience || [],
              projects: parsedRes.data.projects || [],
              education: parsedRes.data.education || [],
              email: parsedRes.data.contact_info?.emails?.[0] || '',
              phone: parsedRes.data.contact_info?.phones?.[0] || '',
            };
          } catch (err) {
            console.error('Error fetching resume:', item.resume_id, err);
            return null;
          }
        })
      );

      setResumes(prev => [...prev, ...resumeData.filter(r => r !== null)]);
      setFiles([]);
      alert(`Uploaded ${uploadRes.data.success_count} resumes!`);
    } catch (err) {
      console.error('Error:', err);
      alert('Error: ' + err.message);
    } finally {
      setUploading(false);
    }
  };

  // Filter resumes
  const filteredResumes = resumes.filter(r => {
    if (minScore > 0 && r.score < minScore) return false;
    if (skillFilter) {
      const searchTerms = skillFilter.toLowerCase().split(',').map(s => s.trim()).filter(s => s);
      const resumeSkills = r.skills.map(s => s.toLowerCase());
      return searchTerms.some(term => 
        resumeSkills.some(skill => skill.includes(term))
      );
    }
    return true;
  }).sort((a, b) => b.score - a.score);

  const categorizedSkillsForResume = (skills) => categorizeSkills(skills);

  return (
    <div>
      {/* Section Header */}
      <div style={{ marginBottom: '32px' }}>
        <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#f1f5f9', margin: '0 0 8px 0' }}>
          Resume Manager
        </h2>
        <p style={{ color: '#94a3b8', fontSize: '16px', margin: 0 }}>
          Batch upload resumes, filter by skills & score, and quickly find the best candidates
        </p>
      </div>

      {/* Upload Area */}
      <label
        style={{
          display: 'block', padding: '48px 32px', textAlign: 'center', cursor: 'pointer',
          border: `2px dashed ${dragOver ? '#6366f1' : '#475569'}`, borderRadius: '16px',
          background: dragOver ? 'rgba(99,102,241,0.1)' : 'rgba(51,65,85,0.5)',
          transition: 'all 0.3s ease', marginBottom: '24px',
        }}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); setFiles(Array.from(e.dataTransfer.files)); }}
      >
        <input type="file" accept=".pdf,.doc,.docx" multiple style={{ display: 'none' }} onChange={handleFilesChange} />
        <div style={{
          width: '80px', height: '80px', borderRadius: '20px', margin: '0 auto 20px',
          background: files.length > 0 ? 'linear-gradient(135deg, #10b981 0%, #34d399 100%)' : 'linear-gradient(135deg, #475569 0%, #64748b 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '36px',
        }}>
          {files.length > 0 ? '✓' : '📚'}
        </div>
        <div style={{ fontSize: '18px', fontWeight: '600', color: '#e2e8f0', marginBottom: '8px' }}>
          {files.length > 0 ? `${files.length} file(s) selected` : 'Drop multiple resumes here or click to browse'}
        </div>
        <div style={{ fontSize: '14px', color: '#64748b' }}>
          Supports PDF, DOC, DOCX • Select multiple files at once
        </div>
      </label>

      {/* Upload Button */}
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <button
          onClick={handleBulkUpload}
          disabled={uploading || files.length === 0}
          style={{
            padding: '16px 48px', fontSize: '16px', fontWeight: '600', border: 'none',
            borderRadius: '12px', cursor: uploading || files.length === 0 ? 'not-allowed' : 'pointer',
            background: uploading || files.length === 0 ? '#475569' : 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
            color: 'white', transition: 'all 0.3s ease',
            boxShadow: uploading || files.length === 0 ? 'none' : '0 10px 30px rgba(99,102,241,0.4)',
            opacity: uploading || files.length === 0 ? 0.6 : 1,
          }}
        >
          {uploading ? '⏳ Processing Resumes...' : `📤 Upload ${files.length > 0 ? files.length + ' Resume(s)' : 'Resumes'}`}
        </button>
      </div>

      {/* Filters Bar */}
      {resumes.length > 0 && (
        <div style={{
          display: 'flex', gap: '20px', flexWrap: 'wrap', alignItems: 'flex-end',
          padding: '24px', background: 'rgba(51,65,85,0.5)', borderRadius: '16px',
          marginBottom: '32px', border: '1px solid rgba(71,85,105,0.5)',
        }}>
          <div style={{ flex: 2, minWidth: '250px' }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              🔍 Filter by Skills
            </label>
            <input
              type="text"
              placeholder="e.g. Python, React, AWS (comma-separated)"
              value={skillFilter}
              onChange={(e) => setSkillFilter(e.target.value)}
              style={{
                width: '100%', padding: '14px 18px', borderRadius: '10px',
                border: '2px solid #475569', background: 'rgba(30,41,59,0.8)',
                color: '#f1f5f9', fontSize: '14px', outline: 'none',
                transition: 'border-color 0.2s',
              }}
            />
          </div>
          <div style={{ flex: 1, minWidth: '150px' }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: '600', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              📊 Min Score
            </label>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <input
                type="range"
                min="0"
                max="100"
                value={minScore}
                onChange={(e) => setMinScore(Number(e.target.value))}
                style={{ flex: 1, accentColor: '#6366f1' }}
              />
              <span style={{ 
                minWidth: '40px', textAlign: 'center', padding: '8px 12px', borderRadius: '8px',
                background: 'rgba(99,102,241,0.2)', color: '#a5b4fc', fontWeight: '600',
              }}>
                {minScore}
              </span>
            </div>
          </div>
          <div style={{
            padding: '14px 20px', borderRadius: '10px', background: 'rgba(99,102,241,0.15)',
            border: '1px solid rgba(99,102,241,0.3)',
          }}>
            <span style={{ color: '#a5b4fc', fontWeight: '600' }}>
              {filteredResumes.length}
            </span>
            <span style={{ color: '#64748b', marginLeft: '4px' }}>
              of {resumes.length} candidates
            </span>
          </div>
        </div>
      )}

      {/* Resume Cards Grid */}
      {filteredResumes.length > 0 && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '20px' }}>
          {filteredResumes.map((r, i) => {
            const gradeInfo = getGradeInfo(r.grade);
            return (
              <div
                key={r.id}
                onClick={() => setSelectedResume(selectedResume?.id === r.id ? null : r)}
                style={{
                  background: 'rgba(51,65,85,0.5)', borderRadius: '16px', padding: '24px',
                  border: selectedResume?.id === r.id ? '2px solid #6366f1' : '1px solid rgba(71,85,105,0.5)',
                  cursor: 'pointer', transition: 'all 0.3s ease',
                  transform: selectedResume?.id === r.id ? 'scale(1.02)' : 'scale(1)',
                }}
              >
                {/* Header with rank, name, score */}
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
                  {/* Rank Badge */}
                  <div style={{
                    width: '36px', height: '36px', borderRadius: '10px',
                    background: i === 0 ? 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%)' :
                               i === 1 ? 'linear-gradient(135deg, #94a3b8 0%, #64748b 100%)' :
                               i === 2 ? 'linear-gradient(135deg, #d97706 0%, #b45309 100%)' : '#334155',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    color: i < 3 ? '#1e293b' : '#94a3b8', fontWeight: '800', fontSize: '14px',
                  }}>
                    {i + 1}
                  </div>
                  
                  {/* Name & Email */}
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '17px', fontWeight: '700', color: '#f1f5f9' }}>{r.name}</div>
                    {r.email && (
                      <div style={{ fontSize: '13px', color: '#64748b', marginTop: '2px' }}>{r.email}</div>
                    )}
                  </div>
                  
                  {/* Score Circle */}
                  <div style={{
                    width: '56px', height: '56px', borderRadius: '14px',
                    background: getGradient(r.score),
                    display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
                    boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
                  }}>
                    <div style={{ fontSize: '20px', fontWeight: '800', color: 'white' }}>{Math.round(r.score)}</div>
                    <div style={{ fontSize: '9px', color: 'rgba(255,255,255,0.8)', fontWeight: '600' }}>{r.grade}</div>
                  </div>
                </div>

                {/* Quick Stats */}
                <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
                  <span style={{
                    padding: '6px 12px', borderRadius: '8px', fontSize: '12px', fontWeight: '600',
                    background: 'rgba(99,102,241,0.15)', color: '#a5b4fc',
                  }}>
                    💼 {r.experience.length} positions
                  </span>
                  <span style={{
                    padding: '6px 12px', borderRadius: '8px', fontSize: '12px', fontWeight: '600',
                    background: 'rgba(139,92,246,0.15)', color: '#c4b5fd',
                  }}>
                    🛠️ {r.skills.length} skills
                  </span>
                  {r.projects.length > 0 && (
                    <span style={{
                      padding: '6px 12px', borderRadius: '8px', fontSize: '12px', fontWeight: '600',
                      background: 'rgba(16,185,129,0.15)', color: '#6ee7b7',
                    }}>
                      🚀 {r.projects.length} projects
                    </span>
                  )}
                </div>

                {/* Top Skills */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {r.skills.slice(0, 5).map((skill, j) => (
                    <span key={j} style={{
                      padding: '5px 12px', borderRadius: '6px', fontSize: '12px', fontWeight: '500',
                      background: 'rgba(30,41,59,0.8)', color: '#cbd5e1',
                    }}>
                      {skill}
                    </span>
                  ))}
                  {r.skills.length > 5 && (
                    <span style={{
                      padding: '5px 12px', borderRadius: '6px', fontSize: '12px',
                      color: '#64748b',
                    }}>
                      +{r.skills.length - 5}
                    </span>
                  )}
                </div>

                {/* Expanded Details */}
                {selectedResume?.id === r.id && (
                  <div style={{ marginTop: '20px', paddingTop: '20px', borderTop: '1px solid rgba(71,85,105,0.5)' }}>
                    {/* Pros & Cons Mini */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                      <div>
                        <div style={{ fontSize: '12px', fontWeight: '600', color: '#10b981', marginBottom: '8px', textTransform: 'uppercase' }}>
                          ✓ Top Strengths
                        </div>
                        {r.strengths.slice(0, 3).map((s, j) => (
                          <div key={j} style={{ fontSize: '12px', color: '#6ee7b7', marginBottom: '4px', paddingLeft: '8px', borderLeft: '2px solid #10b981' }}>
                            {s.length > 50 ? s.substring(0, 50) + '...' : s}
                          </div>
                        ))}
                      </div>
                      <div>
                        <div style={{ fontSize: '12px', fontWeight: '600', color: '#f59e0b', marginBottom: '8px', textTransform: 'uppercase' }}>
                          💡 To Improve
                        </div>
                        {r.improvements.slice(0, 3).map((s, j) => (
                          <div key={j} style={{ fontSize: '12px', color: '#fcd34d', marginBottom: '4px', paddingLeft: '8px', borderLeft: '2px solid #f59e0b' }}>
                            {s.length > 50 ? s.substring(0, 50) + '...' : s}
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Experience Highlights */}
                    {r.experience.length > 0 && (
                      <div>
                        <div style={{ fontSize: '12px', fontWeight: '600', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase' }}>
                          💼 Latest Experience
                        </div>
                        {r.experience.slice(0, 2).map((exp, j) => (
                          <div key={j} style={{ fontSize: '13px', color: '#e2e8f0', marginBottom: '6px' }}>
                            <span style={{ fontWeight: '600' }}>{exp.title}</span>
                            {exp.company && <span style={{ color: '#a5b4fc' }}> at {exp.company}</span>}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Empty State */}
      {resumes.length === 0 && (
        <div style={{
          textAlign: 'center', padding: '80px 40px', background: 'rgba(51,65,85,0.3)',
          borderRadius: '20px', border: '2px dashed #475569',
        }}>
          <div style={{ fontSize: '64px', marginBottom: '24px', opacity: 0.6 }}>📭</div>
          <div style={{ fontSize: '20px', fontWeight: '600', color: '#e2e8f0', marginBottom: '8px' }}>
            No resumes uploaded yet
          </div>
          <div style={{ color: '#64748b', fontSize: '15px' }}>
            Upload some resumes to start comparing candidates
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
