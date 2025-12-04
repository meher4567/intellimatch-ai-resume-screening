import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { Card, Button, ProgressBar, Badge } from '../components';
import api from '../api/config';

function ResumeUpload() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending',
      progress: 0,
    }));
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
    if (files.length === 0) {
      toast.error('Please select files to upload');
      return;
    }

    setUploading(true);
    setUploadResults(null);

    const formData = new FormData();
    files.forEach(({ file }) => {
      formData.append('files', file);
    });

    try {
      const response = await api.post('/api/v1/resumes/batch-upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setFiles(prev => prev.map(f => ({ ...f, progress, status: 'uploading' })));
        },
      });

      const data = response.data;
      setUploadResults(data);
      
      // Update file statuses
      setFiles(prev => prev.map(f => ({ ...f, status: 'success', progress: 100 })));
      
      toast.success(`Successfully processed ${data.successful} out of ${data.total} resumes!`);
      
      // Clear files after a delay
      setTimeout(() => {
        setFiles([]);
        setUploadResults(null);
      }, 5000);
      
    } catch (error) {
      console.error('Upload error:', error);
      setFiles(prev => prev.map(f => ({ ...f, status: 'error' })));
      toast.error(error.response?.data?.detail || 'Failed to upload resumes');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Upload Resumes</h1>
        <p className="text-gray-600 mt-2">Upload and process candidate resumes using AI</p>
      </div>

      {/* Upload Results */}
      {uploadResults && (
        <Card className="mb-6 bg-green-50 border border-green-200">
          <div className="flex items-center">
            <CheckCircle className="w-6 h-6 text-green-600 mr-3" />
            <div>
              <h3 className="font-semibold text-green-800">Upload Complete!</h3>
              <p className="text-sm text-green-700">
                Successfully processed {uploadResults.successful} out of {uploadResults.total} resumes
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Dropzone */}
      <Card className="mb-6">
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-all ${
            isDragActive 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-16 h-16 mx-auto mb-4 text-gray-400" />
          {isDragActive ? (
            <p className="text-lg text-blue-600 font-medium">Drop the files here...</p>
          ) : (
            <>
              <p className="text-lg text-gray-700 font-medium mb-2">
                Drag & drop resume files here
              </p>
              <p className="text-sm text-gray-500 mb-4">
                or click to browse your computer
              </p>
              <Button variant="outline" size="sm">
                Choose Files
              </Button>
              <p className="text-xs text-gray-400 mt-4">
                Supported formats: PDF, DOC, DOCX • Max 5MB per file
              </p>
            </>
          )}
        </div>
      </Card>

      {/* File List */}
      {files.length > 0 && (
        <Card title={`Selected Files (${files.length})`}>
          <div className="space-y-3">
            {files.map(({ file, id, status, progress }) => (
              <div key={id} className="flex items-center p-3 bg-gray-50 rounded-lg">
                <FileText className="w-8 h-8 text-blue-600 mr-3" />
                <div className="flex-1 min-w-0">
                  <p className="font-medium text-gray-800 truncate">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                  {status === 'uploading' && (
                    <ProgressBar value={progress} className="mt-2" />
                  )}
                </div>
                <div className="ml-4 flex items-center">
                  {status === 'pending' && (
                    <button
                      onClick={() => removeFile(id)}
                      className="text-gray-400 hover:text-red-600"
                    >
                      <XCircle className="w-5 h-5" />
                    </button>
                  )}
                  {status === 'uploading' && (
                    <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                  )}
                  {status === 'success' && (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  )}
                  {status === 'error' && (
                    <XCircle className="w-5 h-5 text-red-600" />
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 flex justify-end space-x-3">
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
              Upload & Process
            </Button>
          </div>
        </Card>
      )}

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <Card hover>
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-800 mb-2">Smart Parsing</h3>
            <p className="text-sm text-gray-600">
              AI extracts skills, experience, education, and more from resumes automatically
            </p>
          </div>
        </Card>

        <Card hover>
          <div className="text-center">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <CheckCircle className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="font-semibold text-gray-800 mb-2">Quality Scoring</h3>
            <p className="text-sm text-gray-600">
              Each resume gets a quality score based on completeness and clarity
            </p>
          </div>
        </Card>

        <Card hover>
          <div className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Upload className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-800 mb-2">Batch Processing</h3>
            <p className="text-sm text-gray-600">
              Upload multiple resumes at once and process them in parallel
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}

export default ResumeUpload;
