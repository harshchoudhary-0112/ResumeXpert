/**
 * Analyze page — two-panel layout for resume upload + JD input,
 * with analyze button that triggers the full pipeline.
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ResumeUploader from '../components/ResumeUploader';
import { resumeAPI, jobAPI, analysisAPI } from '../services/api';
import {
  FileText, Briefcase, Search, Loader2, ChevronDown,
  Sparkles, ArrowRight, AlertCircle,
} from 'lucide-react';
import toast from 'react-hot-toast';

export default function Analyze() {
  const navigate = useNavigate();

  // Resume state
  const [selectedResumeId, setSelectedResumeId] = useState(null);
  const [existingResumes, setExistingResumes] = useState([]);
  const [useExisting, setUseExisting] = useState(false);

  // JD state
  const [jobTitle, setJobTitle] = useState('');
  const [company, setCompany] = useState('');
  const [jdText, setJdText] = useState('');

  // Analysis state
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    loadExistingResumes();
  }, []);

  const loadExistingResumes = async () => {
    try {
      const res = await resumeAPI.list();
      setExistingResumes(res.data);
    } catch (error) {
      console.error('Failed to load resumes:', error);
    }
  };

  const handleUploadSuccess = (data) => {
    setSelectedResumeId(data.id);
    setUseExisting(false);
    loadExistingResumes();
  };

  const handleAnalyze = async () => {
    if (!selectedResumeId) {
      toast.error('Please upload or select a resume');
      return;
    }
    if (!jdText || jdText.trim().length < 50) {
      toast.error('Please enter a job description (at least 50 characters)');
      return;
    }

    setAnalyzing(true);
    try {
      // Step 1: Create JD
      const jdRes = await jobAPI.create({
        title: jobTitle || null,
        company: company || null,
        description: jdText,
      });
      const jobId = jdRes.data.id;

      // Step 2: Run analysis
      const analysisRes = await analysisAPI.run({
        resume_id: selectedResumeId,
        job_id: jobId,
      });

      toast.success('Analysis complete!');
      navigate(`/results/${analysisRes.data.id}`);
    } catch (error) {
      const message = error.response?.data?.detail || 'Analysis failed. Please try again.';
      toast.error(message);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-3xl md:text-4xl font-bold font-display text-white mb-3">
            <span className="gradient-text">Analyze</span> Your Resume
          </h1>
          <p className="text-dark-400 max-w-lg mx-auto">
            Upload your resume and paste the target job description to get a comprehensive AI-powered analysis.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* ── Left Panel: Resume ────────────────────────── */}
          <div className="glass-card p-6 animate-slide-up">
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-primary-500/15 flex items-center justify-center">
                <FileText className="w-5 h-5 text-primary-400" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Resume</h2>
                <p className="text-xs text-dark-400">Upload or select an existing resume</p>
              </div>
            </div>

            {/* Upload new */}
            <ResumeUploader onUploadSuccess={handleUploadSuccess} />

            {/* Or select existing */}
            {existingResumes.length > 0 && (
              <div className="mt-5">
                <div className="flex items-center gap-3 mb-3">
                  <div className="h-px flex-1 bg-dark-700/50" />
                  <span className="text-xs text-dark-500 uppercase tracking-wider">or select existing</span>
                  <div className="h-px flex-1 bg-dark-700/50" />
                </div>

                <div className="relative">
                  <select
                    value={useExisting ? selectedResumeId || '' : ''}
                    onChange={(e) => {
                      const id = parseInt(e.target.value);
                      if (id) {
                        setSelectedResumeId(id);
                        setUseExisting(true);
                      }
                    }}
                    className="input-field appearance-none pr-10 cursor-pointer"
                  >
                    <option value="">Choose a previously uploaded resume...</option>
                    {existingResumes.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.filename} {r.name ? `(${r.name})` : ''} — {new Date(r.created_at).toLocaleDateString()}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400 pointer-events-none" />
                </div>
              </div>
            )}

            {/* Selection indicator */}
            {selectedResumeId && (
              <div className="mt-4 flex items-center gap-2 text-sm text-emerald-400">
                <Sparkles className="w-4 h-4" />
                Resume #{selectedResumeId} selected
              </div>
            )}
          </div>

          {/* ── Right Panel: Job Description ──────────────── */}
          <div className="glass-card p-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-xl bg-accent-500/15 flex items-center justify-center">
                <Briefcase className="w-5 h-5 text-accent-400" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-white">Job Description</h2>
                <p className="text-xs text-dark-400">Paste the target job description</p>
              </div>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-1.5">Job Title</label>
                  <input
                    type="text"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)}
                    className="input-field !py-2.5 text-sm"
                    placeholder="e.g. Senior Python Dev"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-1.5">Company</label>
                  <input
                    type="text"
                    value={company}
                    onChange={(e) => setCompany(e.target.value)}
                    className="input-field !py-2.5 text-sm"
                    placeholder="e.g. TechCorp"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-dark-300 mb-1.5">
                  Description <span className="text-red-400">*</span>
                </label>
                <textarea
                  value={jdText}
                  onChange={(e) => setJdText(e.target.value)}
                  className="textarea-field !min-h-[260px] text-sm"
                  placeholder="Paste the full job description here...&#10;&#10;Include responsibilities, required skills, qualifications, and experience requirements for the best analysis."
                />
                <div className="flex items-center justify-between mt-1.5">
                  <span className={`text-xs ${jdText.length < 50 ? 'text-dark-500' : 'text-dark-400'}`}>
                    {jdText.length} characters
                  </span>
                  {jdText.length > 0 && jdText.length < 50 && (
                    <span className="text-xs text-amber-400 flex items-center gap-1">
                      <AlertCircle className="w-3 h-3" /> Minimum 50 characters
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ── Analyze Button ─────────────────────────────── */}
        <div className="mt-8 text-center">
          <button
            onClick={handleAnalyze}
            disabled={analyzing || !selectedResumeId || jdText.length < 50}
            className="btn-primary text-lg !px-10 !py-4 inline-flex items-center gap-3 group"
          >
            {analyzing ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <Search className="w-5 h-5" />
                Run Analysis
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
          {analyzing && (
            <p className="text-sm text-dark-400 mt-3 animate-pulse">
              Running NLP pipeline, semantic matching, ATS checks, and ML classification...
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
