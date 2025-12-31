import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, XCircle, Loader2, Sparkles, Zap, Shield, ChevronDown, ChevronUp, Mail, Phone, Briefcase, GraduationCap, Code } from 'lucide-react';
import toast from 'react-hot-toast';
import { Card, Button } from '../components';
import api from '../api/config';

function ResumeUpload() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState(null);
  const [expandedResume, setExpandedResume] = useState(null);
  const [resumeDetails, setResumeDetails] = useState({});
  const [loadingDetails, setLoadingDetails] = useState({});

  const onDrop = useCallback((acceptedFiles) => {
    console.log('📁 FILES DROPPED:', acceptedFiles);
    console.log('Number of files:', acceptedFiles.length);
    
    const newFiles = acceptedFiles.map(file => {
      console.log('File:', file.name, file.type, file.size);
      return {
        file,
        id: Math.random().toString(36).substr(2, 9),
        status: 'pending',
        progress: 0,
      };
    });
    setFiles(prev => [...prev, ...newFiles]);
    toast.success(`${acceptedFiles.length} file(s) added`);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    multiple: true,
  });

  const removeFile = (id) => {
    setFiles(files.filter(f => f.id !== id));
    toast.success('File removed');
  };

  const uploadResumes = async () => {
    console.log('🚀 UPLOAD BUTTON CLICKED');
    console.log('Files array:', files);
    console.log('Files length:', files.length);
    
    if (files.length === 0) {
      console.log('❌ No files selected');
      toast.error('Please select files to upload');
      return;
    }

    console.log('✅ Starting upload...');
    setUploading(true);
    setUploadResults(null);
    setResumeDetails({});
    setExpandedResume(null);

    const formData = new FormData();
    files.forEach(({ file }, index) => {
      console.log(`📄 Adding file ${index}:`, file.name, file.type, file.size);
      formData.append('files', file);
    });

    console.log('📤 Sending request to /api/v1/resumes/batch-upload...');
    
    try {
      const response = await api.post('/api/v1/resumes/batch-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          console.log(`📊 Upload progress: ${progress}%`);
          setFiles(prev => prev.map(f => ({ ...f, progress, status: 'uploading' })));
        },
      });

      console.log('✅ RESPONSE RECEIVED');
      console.log('response:', response);
      console.log('response.data:', response.data);
      console.log('JSON:', JSON.stringify(response.data, null, 2));
      
      const data = response.data;
      console.log('Setting uploadResults to:', data);
      
      setUploadResults(data);
      setFiles(prev => prev.map(f => ({ ...f, status: 'success', progress: 100 })));
      
      const successCount = data?.success_count ?? data?.successful?.length ?? 0;
      const totalCount = data?.total ?? 1;
      console.log(`🎉 Success: ${successCount}/${totalCount}`);
      toast.success(`Successfully processed ${successCount} out of ${totalCount} resumes!`);
      
    } catch (error) {
      console.error('Upload error:', error);
      setFiles(prev => prev.map(f => ({ ...f, status: 'error' })));
      toast.error(error.response?.data?.detail || 'Failed to upload resumes');
    } finally {
      setUploading(false);
    }
  };

  const fetchResumeDetails = async (resumeId) => {
    if (resumeDetails[resumeId]) {
      // Already fetched, just toggle
      setExpandedResume(expandedResume === resumeId ? null : resumeId);
      return;
    }

    setLoadingDetails(prev => ({ ...prev, [resumeId]: true }));
    
    try {
      const [qualityResp, parsedResp] = await Promise.all([
        api.get(`/api/v1/resumes/${resumeId}/quality?refresh=true`),
        api.get(`/api/v1/resumes/${resumeId}/parsed`)
      ]);
      
      setResumeDetails(prev => ({
        ...prev,
        [resumeId]: {
          quality: qualityResp.data,
          parsed: parsedResp.data
        }
      }));
      setExpandedResume(resumeId);
    } catch (err) {
      console.error(`Error fetching details for resume ${resumeId}:`, err);
      toast.error('Failed to fetch resume details');
    } finally {
      setLoadingDetails(prev => ({ ...prev, [resumeId]: false }));
    }
  };

  const clearResults = () => {
    setUploadResults(null);
    setFiles([]);
    setResumeDetails({});
    setExpandedResume(null);
  };

  return (
    <div className="p-8 min-h-screen animate-fade-in">
      {/* Header */}
      <div className="mb-8 animate-fade-in-down">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-12 h-12 gradient-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary-500/30">
            <Upload className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gray-800">Upload Resumes</h1>
            <p className="text-gray-600 text-lg">Upload and process candidate resumes with AI ✨</p>
          </div>
        </div>
      </div>

      {/* Upload Results */}
      {uploadResults && (
        <div className="mb-6 space-y-4">
          {/* Summary Card */}
          <Card className="bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200" hover={false}>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="w-12 h-12 rounded-xl bg-green-500 flex items-center justify-center mr-4 shadow-lg shadow-green-500/30">
                  <CheckCircle className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-green-800 text-lg">🎉 Upload Complete!</h3>
                  <p className="text-sm text-green-700">
                    Successfully processed <span className="font-bold">{uploadResults.success_count}</span> out of <span className="font-bold">{uploadResults.total}</span> resumes
                  </p>
                </div>
              </div>
              <Button variant="secondary" onClick={clearResults}>
                Clear Results
              </Button>
            </div>
          </Card>

          {/* Individual Resume Cards with View Details Button */}
          {uploadResults.successful && uploadResults.successful.map(item => (
            <Card key={item.resume_id} hover={false} className="overflow-hidden">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-violet-100 flex items-center justify-center">
                    <FileText className="w-6 h-6 text-violet-600" />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-800 text-lg">{item.name || item.filename}</h3>
                    <p className="text-sm text-gray-500">Resume ID: {item.resume_id} • Filename: {item.filename}</p>
                  </div>
                </div>
                <Button 
                  variant="primary"
                  onClick={() => fetchResumeDetails(item.resume_id)}
                  disabled={loadingDetails[item.resume_id]}
                >
                  {loadingDetails[item.resume_id] ? (
                    <><Loader2 className="w-4 h-4 animate-spin mr-2" /> Loading...</>
                  ) : expandedResume === item.resume_id ? (
                    <><ChevronUp className="w-4 h-4 mr-2" /> Hide Details</>
                  ) : (
                    <><ChevronDown className="w-4 h-4 mr-2" /> View Details</>
                  )}
                </Button>
              </div>

              {/* Expanded Details */}
              {expandedResume === item.resume_id && resumeDetails[item.resume_id] && (
                <div className="mt-6 pt-6 border-t border-gray-200 space-y-6">
                  {(() => {
                    const { quality: qa, parsed } = resumeDetails[item.resume_id];
                    return (
                      <>
                        {/* Score & Contact Row */}
                        <div className="flex flex-col md:flex-row gap-6">
                          {qa && (
                            <div className="flex-shrink-0 flex items-center gap-4 p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl">
                              <div className={`w-20 h-20 rounded-full bg-gradient-to-br ${
                                qa.score >= 80 ? 'from-green-500 to-emerald-500' :
                                qa.score >= 60 ? 'from-blue-500 to-indigo-500' :
                                qa.score >= 40 ? 'from-yellow-500 to-orange-500' :
                                'from-red-500 to-pink-500'
                              } flex items-center justify-center shadow-lg`}>
                                <div className="text-center text-white">
                                  <p className="text-2xl font-bold">{Math.round(qa.score)}</p>
                                  <p className="text-xs opacity-90">/100</p>
                                </div>
                              </div>
                              <div>
                                <div className={`px-3 py-1 rounded-full font-bold text-lg ${
                                  qa.grade?.startsWith('A') ? 'text-green-600 bg-green-100' :
                                  qa.grade?.startsWith('B') ? 'text-blue-600 bg-blue-100' :
                                  qa.grade?.startsWith('C') ? 'text-yellow-600 bg-yellow-100' :
                                  'text-red-600 bg-red-100'
                                }`}>
                                  Grade: {qa.grade}
                                </div>
                              </div>
                            </div>
                          )}

                          <div className="flex-1">
                            <h4 className="font-bold text-gray-800 text-xl mb-2">{parsed?.name || 'Unknown'}</h4>
                            {parsed?.contact_info && (
                              <div className="flex flex-wrap gap-4 text-sm">
                                {parsed.contact_info.emails?.[0] && (
                                  <span className="flex items-center gap-1 text-gray-600">
                                    <Mail className="w-4 h-4" /> {parsed.contact_info.emails[0]}
                                  </span>
                                )}
                                {parsed.contact_info.phones?.[0] && (
                                  <span className="flex items-center gap-1 text-gray-600">
                                    <Phone className="w-4 h-4" /> {parsed.contact_info.phones[0]}
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        </div>

                        {/* Quality Breakdown */}
                        {qa && (
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="p-4 bg-green-50 rounded-xl border border-green-200">
                              <h4 className="font-bold text-green-800 mb-2">✓ Strengths</h4>
                              <ul className="space-y-1">
                                {qa.strengths?.slice(0,5).map((s, i) => (
                                  <li key={i} className="text-sm text-green-700">• {s}</li>
                                ))}
                              </ul>
                            </div>
                            <div className="p-4 bg-orange-50 rounded-xl border border-orange-200">
                              <h4 className="font-bold text-orange-800 mb-2">→ To Improve</h4>
                              <ul className="space-y-1">
                                {qa.improvements?.slice(0,5).map((s, i) => (
                                  <li key={i} className="text-sm text-orange-700">• {s}</li>
                                ))}
                              </ul>
                            </div>
                          </div>
                        )}

                        {/* Experience */}
                        {parsed?.experience?.length > 0 && (
                          <div>
                            <h4 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                              <Briefcase className="w-5 h-5 text-violet-500" /> Experience ({parsed.experience.length} positions)
                            </h4>
                            <div className="space-y-3">
                              {parsed.experience.slice(0,4).map((exp, i) => (
                                <div key={i} className="p-3 bg-gray-50 rounded-lg border-l-4 border-violet-500">
                                  <p className="font-semibold">{exp.title || 'Position'}</p>
                                  <p className="text-sm text-violet-600">{exp.company || 'Company'}</p>
                                  {exp.achievements?.slice(0,2).map((a, j) => (
                                    <p key={j} className="text-sm text-gray-600 mt-1">• {a}</p>
                                  ))}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Education */}
                        {parsed?.sections?.education?.content && (
                          <div>
                            <h4 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                              <GraduationCap className="w-5 h-5 text-blue-500" /> Education
                            </h4>
                            <div className="p-3 bg-blue-50 rounded-lg">
                              <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
                                {parsed.sections.education.content.substring(0, 500)}
                              </pre>
                            </div>
                          </div>
                        )}

                        {/* Skills */}
                        {parsed?.skills?.all_skills?.length > 0 && (
                          <div>
                            <h4 className="font-bold text-gray-800 mb-3 flex items-center gap-2">
                              <Code className="w-5 h-5 text-indigo-500" /> Skills ({parsed.skills.all_skills.length})
                            </h4>
                            <div className="flex flex-wrap gap-2">
                              {parsed.skills.all_skills.slice(0,25).map((skill, i) => (
                                <span key={i} className="px-3 py-1 bg-gradient-to-r from-violet-100 to-purple-100 text-violet-700 rounded-full text-sm font-medium border border-violet-200">
                                  {skill}
                                </span>
                              ))}
                              {parsed.skills.all_skills.length > 25 && (
                                <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">
                                  +{parsed.skills.all_skills.length - 25} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </>
                    );
                  })()}
                </div>
              )}
            </Card>
          ))}

          {/* Failed uploads */}
          {uploadResults.failed && uploadResults.failed.length > 0 && (
            <Card className="bg-red-50 border-2 border-red-200" hover={false}>
              <h3 className="font-bold text-red-800 mb-2">❌ Failed Uploads</h3>
              {uploadResults.failed.map((item, i) => (
                <p key={i} className="text-sm text-red-700">• {item.filename}: {item.error}</p>
              ))}
            </Card>
          )}
        </div>
      )}

      {/* Dropzone */}
      <Card className="mb-6" hover={false}>
        <div
          {...getRootProps()}
          className={`border-3 border-dashed rounded-2xl p-16 text-center cursor-pointer transition-all duration-300 ${
            isDragActive 
              ? 'border-primary-500 bg-primary-50 scale-[1.02] shadow-glow-primary' 
              : 'border-gray-300 hover:border-primary-400 hover:bg-primary-50/50'
          }`}
        >
          <input {...getInputProps()} />
          <div className={`w-20 h-20 mx-auto mb-6 rounded-2xl flex items-center justify-center transition-all duration-300 ${
            isDragActive 
              ? 'gradient-primary shadow-lg shadow-primary-500/40 animate-float' 
              : 'bg-gray-100'
          }`}>
            <Upload className={`w-10 h-10 ${isDragActive ? 'text-white' : 'text-gray-400'}`} />
          </div>
          {isDragActive ? (
            <p className="text-xl text-primary-600 font-bold">Drop the files here...</p>
          ) : (
            <>
              <p className="text-xl text-gray-800 font-bold mb-2">
                Drag & drop resume files here
              </p>
              <p className="text-gray-500 mb-6">
                or click to browse your computer
              </p>
              <Button variant="outline" size="md">
                Choose Files
              </Button>
              <p className="text-sm text-gray-400 mt-6">
                📄 Supported formats: PDF, DOC, DOCX • Max 5MB per file
              </p>
            </>
          )}
        </div>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <Card title={`📁 Selected Files (${files.length})`} hover={false}>
          <div className="space-y-3">
            {files.map(({ file, id, status, progress }) => (
              <div 
                key={id} 
                className={`flex items-center p-4 rounded-xl transition-all duration-300 ${
                  status === 'success' ? 'bg-green-50 border border-green-200' :
                  status === 'error' ? 'bg-red-50 border border-red-200' :
                  'bg-gray-50 border border-gray-200 hover:bg-gray-100'
                }`}
              >
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center mr-4 ${
                  status === 'success' ? 'bg-green-100' :
                  status === 'error' ? 'bg-red-100' :
                  'bg-primary-100'
                }`}>
                  <FileText className={`w-6 h-6 ${
                    status === 'success' ? 'text-green-600' :
                    status === 'error' ? 'text-red-600' :
                    'text-primary-600'
                  }`} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-semibold text-gray-800 truncate">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  {status === 'uploading' && (
                    <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  )}
                </div>
                <div className="ml-4 flex items-center">
                  {status === 'pending' && (
                    <button
                      onClick={() => removeFile(id)}
                      className="w-10 h-10 rounded-lg hover:bg-red-100 flex items-center justify-center text-gray-400 hover:text-red-600 transition-colors"
                    >
                      <XCircle className="w-5 h-5" />
                    </button>
                  )}
                  {status === 'uploading' && (
                    <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
                      <Loader2 className="w-5 h-5 text-primary-600 animate-spin" />
                    </div>
                  )}
                  {status === 'success' && (
                    <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    </div>
                  )}
                  {status === 'error' && (
                    <div className="w-10 h-10 rounded-lg bg-red-100 flex items-center justify-center">
                      <XCircle className="w-5 h-5 text-red-600" />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex justify-end gap-4">
            <Button 
              variant="secondary" 
              onClick={() => setFiles([])}
              disabled={uploading}
            >
              Clear All
            </Button>
            <Button 
              onClick={uploadResumes}
              loading={uploading}
              icon={Upload}
            >
              🚀 Upload & Process
            </Button>
          </div>
        </Card>
      )}

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <Card hover={true}>
          <div className="text-center py-4">
            <div className="w-16 h-16 gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary-500/30">
              <Sparkles className="w-8 h-8 text-white" />
            </div>
            <h3 className="font-bold text-gray-800 text-lg mb-2">Smart Parsing</h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              AI extracts skills, experience, education, and more from resumes automatically
            </p>
          </div>
        </Card>

        <Card hover={true}>
          <div className="text-center py-4">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-violet-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-purple-500/30">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <h3 className="font-bold text-gray-800 text-lg mb-2">Quality Scoring</h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              Each resume gets a quality score based on completeness and clarity
            </p>
          </div>
        </Card>

        <Card hover={true}>
          <div className="text-center py-4">
            <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-green-500/30">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h3 className="font-bold text-gray-800 text-lg mb-2">Batch Processing</h3>
            <p className="text-sm text-gray-600 leading-relaxed">
              Upload multiple resumes at once and process them in parallel
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default ResumeUpload;
