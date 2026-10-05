/**
 * ResumeUploader — drag-and-drop resume upload component
 * with file validation and upload progress.
 */

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { resumeAPI } from '../services/api';
import toast from 'react-hot-toast';

const ACCEPTED_TYPES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
};

export default function ResumeUploader({ onUploadSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
    if (rejectedFiles.length > 0) {
      toast.error('Invalid file type. Please upload a PDF or DOCX file.');
      return;
    }

    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];

    // File size check (10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File too large. Maximum size is 10MB.');
      return;
    }

    setUploading(true);
    try {
      const response = await resumeAPI.upload(file);
      setUploadedFile({
        name: file.name,
        size: file.size,
        data: response.data,
      });
      toast.success('Resume uploaded and parsed successfully!');
      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to upload resume';
      toast.error(message);
    } finally {
      setUploading(false);
    }
  }, [onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxFiles: 1,
    disabled: uploading,
  });

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`relative cursor-pointer border-2 border-dashed rounded-2xl p-8 text-center transition-all duration-300
          ${isDragActive && isDragAccept ? 'border-primary-500 bg-primary-500/10 scale-[1.02]' : ''}
          ${isDragReject ? 'border-red-500 bg-red-500/10' : ''}
          ${!isDragActive ? 'border-dark-600/50 hover:border-primary-500/50 hover:bg-dark-800/30' : ''}
          ${uploading ? 'pointer-events-none opacity-60' : ''}
        `}
      >
        <input {...getInputProps()} />

        <div className="flex flex-col items-center gap-3">
          {uploading ? (
            <>
              <Loader2 className="w-12 h-12 text-primary-400 animate-spin" />
              <p className="text-dark-200 font-medium">Parsing resume...</p>
              <p className="text-sm text-dark-400">Extracting text, skills, and sections</p>
            </>
          ) : isDragReject ? (
            <>
              <AlertCircle className="w-12 h-12 text-red-400" />
              <p className="text-red-400 font-medium">Invalid file type</p>
              <p className="text-sm text-dark-400">Only PDF and DOCX files are accepted</p>
            </>
          ) : (
            <>
              <div className="w-16 h-16 rounded-2xl bg-primary-500/10 border border-primary-500/20 flex items-center justify-center">
                <Upload className="w-8 h-8 text-primary-400" />
              </div>
              <div>
                <p className="text-dark-200 font-medium">
                  {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume'}
                </p>
                <p className="text-sm text-dark-400 mt-1">
                  or <span className="text-primary-400 font-medium">browse files</span> • PDF, DOCX up to 10MB
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Uploaded file info */}
      {uploadedFile && !uploading && (
        <div className="glass-card p-4 flex items-center gap-4 animate-slide-up">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/15 flex items-center justify-center">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-dark-400" />
              <span className="text-sm font-medium text-white truncate">{uploadedFile.name}</span>
            </div>
            <div className="flex items-center gap-3 mt-0.5">
              <span className="text-xs text-dark-400">{formatSize(uploadedFile.size)}</span>
              {uploadedFile.data?.parsed_data?.skills?.length > 0 && (
                <span className="text-xs text-primary-400">
                  {uploadedFile.data.parsed_data.skills.length} skills detected
                </span>
              )}
              {uploadedFile.data?.parsed_data?.name && (
                <span className="text-xs text-accent-400">
                  {uploadedFile.data.parsed_data.name}
                </span>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
