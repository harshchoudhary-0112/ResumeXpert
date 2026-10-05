/**
 * History page — list of all past analyses with scores,
 * classification badges, and links to full results.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { analysisAPI } from '../services/api';
import {
  Loader2, FileText, Briefcase, Clock, ArrowRight,
  Search, BarChart3, Trash2,
} from 'lucide-react';

const CLASSIFICATION_STYLES = {
  'Strong Match': 'score-strong',
  'Moderate Match': 'score-moderate',
  'Weak Match': 'score-weak',
  'Poor Match': 'score-poor',
};

export default function History() {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const res = await analysisAPI.history();
      setAnalyses(res.data);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-24 flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-primary-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold font-display text-white">Analysis History</h1>
            <p className="text-dark-400 mt-1">{analyses.length} analyses completed</p>
          </div>
          <Link to="/analyze" className="btn-primary flex items-center gap-2">
            <Search className="w-4 h-4" /> New Analysis
          </Link>
        </div>

        {analyses.length > 0 ? (
          <div className="space-y-3">
            {analyses.map((analysis, i) => (
              <Link
                key={analysis.id}
                to={`/results/${analysis.id}`}
                className="glass-card-hover p-5 flex items-center gap-5 group block animate-slide-up"
                style={{ animationDelay: `${Math.min(i * 0.05, 0.5)}s` }}
              >
                {/* Score circle */}
                <div className="relative w-14 h-14 flex-shrink-0">
                  <svg width="56" height="56" className="-rotate-90">
                    <circle cx="28" cy="28" r="22" fill="none" stroke="rgba(100,116,139,0.15)" strokeWidth="4" />
                    <circle
                      cx="28" cy="28" r="22" fill="none"
                      stroke={
                        analysis.match_score >= 75 ? '#10b981' :
                        analysis.match_score >= 50 ? '#f59e0b' :
                        analysis.match_score >= 30 ? '#f97316' : '#ef4444'
                      }
                      strokeWidth="4" strokeLinecap="round"
                      strokeDasharray={2 * Math.PI * 22}
                      strokeDashoffset={2 * Math.PI * 22 * (1 - analysis.match_score / 100)}
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-sm font-bold text-white">{analysis.match_score.toFixed(0)}</span>
                  </div>
                </div>

                {/* Details */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 flex-wrap">
                    {analysis.resume_filename && (
                      <span className="flex items-center gap-1.5 text-sm text-dark-200">
                        <FileText className="w-3.5 h-3.5 text-primary-400" />
                        <span className="truncate max-w-[150px]">{analysis.resume_filename}</span>
                      </span>
                    )}
                    {analysis.job_title && (
                      <>
                        <span className="text-dark-600">→</span>
                        <span className="flex items-center gap-1.5 text-sm text-dark-200">
                          <Briefcase className="w-3.5 h-3.5 text-accent-400" />
                          <span className="truncate max-w-[150px]">{analysis.job_title}</span>
                        </span>
                      </>
                    )}
                  </div>
                  <div className="flex items-center gap-3 mt-1.5">
                    <span className={CLASSIFICATION_STYLES[analysis.classification] || 'score-badge bg-dark-700 text-dark-300'}>
                      {analysis.classification}
                    </span>
                    <span className="flex items-center gap-1 text-xs text-dark-500">
                      <Clock className="w-3 h-3" />
                      {new Date(analysis.created_at).toLocaleDateString(undefined, {
                        year: 'numeric', month: 'short', day: 'numeric',
                        hour: '2-digit', minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>

                {/* Arrow */}
                <ArrowRight className="w-5 h-5 text-dark-600 group-hover:text-primary-400 group-hover:translate-x-1 transition-all" />
              </Link>
            ))}
          </div>
        ) : (
          <div className="glass-card p-12 text-center">
            <BarChart3 className="w-12 h-12 text-dark-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">No analyses yet</h3>
            <p className="text-dark-400 mb-6">Upload a resume and paste a job description to get started.</p>
            <Link to="/analyze" className="btn-primary inline-flex items-center gap-2">
              <Search className="w-4 h-4" /> Start Your First Analysis
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
