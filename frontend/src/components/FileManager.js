import React, { useState, useEffect } from 'react';
import { fileService } from '../services/apiService';
import { Upload, FileText, Trash2, Search, Download } from 'lucide-react';

const FileManager = ({ workspaceId }) => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [supportedFormats, setSupportedFormats] = useState([]);

  useEffect(() => {
    fetchFiles();
    fetchSupportedFormats();
  }, [workspaceId]);

  const fetchFiles = async () => {
    setLoading(true);
    try {
      const response = await fileService.getFiles(workspaceId);
      setFiles(response);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch files');
    } finally {
      setLoading(false);
    }
  };

  const fetchSupportedFormats = async () => {
    try {
      const response = await fileService.getSupportedFormats(workspaceId);
      setSupportedFormats(response);
    } catch (err) {
      console.error('Failed to fetch supported formats:', err);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      await fileService.uploadFile(workspaceId, formData);
      await fetchFiles(); // Refresh the file list
      setError(null);
      
      // Reset the input
      event.target.value = '';
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteFile = async (fileId) => {
    if (!window.confirm('Are you sure you want to delete this file?')) {
      return;
    }

    try {
      await fileService.deleteFile(fileId);
      await fetchFiles(); // Refresh the file list
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete file');
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    try {
      const response = await fileService.searchFiles(workspaceId, {
        query: searchQuery
      });
      setSearchResults(response);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.message || 'Search failed');
    } finally {
      setSearching(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="file-manager">
      <div className="file-manager-header">
        <h3>File Management</h3>
        
        <div className="upload-section">
          <label htmlFor="file-upload" className="upload-button">
            <Upload size={20} />
            {uploading ? 'Uploading...' : 'Upload File'}
          </label>
          <input
            id="file-upload"
            type="file"
            onChange={handleFileUpload}
            disabled={uploading}
            accept=".txt,.md,.pdf,.doc,.docx"
            style={{ display: 'none' }}
          />
          {supportedFormats.length > 0 && (
            <small className="supported-formats">
              Supported formats: {supportedFormats.join(', ')}
            </small>
          )}
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Search Section */}
      <div className="search-section">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="Search files by content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <button type="submit" disabled={searching} className="search-button">
            <Search size={20} />
            {searching ? 'Searching...' : 'Search'}
          </button>
        </form>
        
        {searchResults.length > 0 && (
          <div className="search-results">
            <h4>Search Results</h4>
            <div className="search-results-list">
              {searchResults.map((result, index) => (
                <div key={index} className="search-result-item">
                  <FileText size={16} />
                  <div className="result-content">
                    <strong>{result.filename}</strong>
                    <p>{result.snippet}</p>
                    <small>Relevance: {(result.score * 100).toFixed(1)}%</small>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Files List */}
      <div className="files-section">
        <h4>Uploaded Files ({files.length})</h4>
        
        {loading ? (
          <div className="loading">Loading files...</div>
        ) : files.length === 0 ? (
          <div className="empty-state">
            <FileText size={48} />
            <h3>No files uploaded yet</h3>
            <p>Upload your first file to start building your knowledge base!</p>
          </div>
        ) : (
          <div className="files-list">
            {files.map((file) => (
              <div key={file.id} className="file-item">
                <div className="file-icon">
                  <FileText size={24} />
                </div>
                <div className="file-info">
                  <h5>{file.filename}</h5>
                  <div className="file-meta">
                    <span>{formatFileSize(file.size)}</span>
                    <span>{formatDate(file.uploaded_at)}</span>
                    {file.status && (
                      <span className={`status ${file.status}`}>
                        {file.status}
                      </span>
                    )}
                  </div>
                </div>
                <div className="file-actions">
                  <button
                    onClick={() => handleDeleteFile(file.id)}
                    className="delete-button"
                    title="Delete file"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FileManager;
