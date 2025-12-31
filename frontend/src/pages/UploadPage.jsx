import React, { useState } from 'react';
import api from '../api/config';

console.log('🔥 UploadPage.jsx LOADED');

function UploadPage() {
  console.log('🔥 UploadPage COMPONENT RENDERED');
  
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    console.log('📁 FILE SELECTED:', e.target.files[0]);
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    console.log('🚀 UPLOAD CLICKED');
    console.log('File:', file);
    
    if (!file) {
      alert('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('files', file);

    console.log('📤 Sending to API...');

    try {
      const response = await api.post('/api/v1/resumes/batch-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      console.log('✅ RESPONSE:', response);
      console.log('✅ DATA:', response.data);
      console.log('✅ JSON:', JSON.stringify(response.data, null, 2));
      
      setResult(response.data);
    } catch (err) {
      console.error('❌ ERROR:', err);
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '32px', marginBottom: '20px' }}>📄 Upload Resume (Debug Page)</h1>
      
      <div style={{ marginBottom: '20px', padding: '20px', border: '2px dashed #ccc', borderRadius: '8px' }}>
        <input 
          type="file" 
          accept=".pdf,.doc,.docx"
          onChange={handleFileChange}
          style={{ fontSize: '16px' }}
        />
      </div>

      {file && (
        <p style={{ marginBottom: '20px', color: 'green' }}>
          ✅ Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
        </p>
      )}

      <button 
        onClick={handleUpload}
        disabled={uploading || !file}
        style={{
          padding: '15px 30px',
          fontSize: '18px',
          backgroundColor: uploading ? '#ccc' : '#4F46E5',
          color: 'white',
          border: 'none',
          borderRadius: '8px',
          cursor: uploading ? 'not-allowed' : 'pointer',
        }}
      >
        {uploading ? '⏳ Uploading...' : '🚀 Upload Resume'}
      </button>

      {error && (
        <div style={{ marginTop: '20px', padding: '20px', backgroundColor: '#FEE2E2', borderRadius: '8px', color: 'red' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: '20px', padding: '20px', backgroundColor: '#D1FAE5', borderRadius: '8px' }}>
          <h3 style={{ marginBottom: '10px' }}>✅ Upload Result:</h3>
          <p><strong>Success Count:</strong> {result.success_count}</p>
          <p><strong>Total:</strong> {result.total}</p>
          
          {result.successful && result.successful.length > 0 && (
            <div style={{ marginTop: '15px' }}>
              <h4>Uploaded Resumes:</h4>
              {result.successful.map((item, i) => (
                <div key={i} style={{ padding: '10px', marginTop: '10px', backgroundColor: 'white', borderRadius: '4px' }}>
                  <p><strong>Name:</strong> {item.name || 'N/A'}</p>
                  <p><strong>Resume ID:</strong> {item.resume_id}</p>
                  <p><strong>Filename:</strong> {item.filename}</p>
                  <button
                    onClick={async () => {
                      console.log('Fetching details for resume:', item.resume_id);
                      try {
                        const [qualityRes, parsedRes] = await Promise.all([
                          api.get(`/api/v1/resumes/${item.resume_id}/quality`),
                          api.get(`/api/v1/resumes/${item.resume_id}/parsed`)
                        ]);
                        console.log('Quality:', qualityRes.data);
                        console.log('Parsed:', parsedRes.data);
                        alert(`Score: ${qualityRes.data.score}, Grade: ${qualityRes.data.grade}\n\nCheck console for full details!`);
                      } catch (e) {
                        console.error('Error fetching details:', e);
                      }
                    }}
                    style={{ marginTop: '10px', padding: '8px 16px', backgroundColor: '#6366F1', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                  >
                    📊 View Details
                  </button>
                </div>
              ))}
            </div>
          )}

          <details style={{ marginTop: '15px' }}>
            <summary style={{ cursor: 'pointer' }}>Raw JSON Response</summary>
            <pre style={{ marginTop: '10px', padding: '10px', backgroundColor: '#F3F4F6', borderRadius: '4px', overflow: 'auto', fontSize: '12px' }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}

export default UploadPage;
