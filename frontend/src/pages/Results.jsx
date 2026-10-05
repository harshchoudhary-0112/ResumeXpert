/**
 * Results page — comprehensive analysis results with score card,
 * breakdowns, skills, ATS, SHAP explanations, and suggestions.
 */

import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { analysisAPI } from '../services/api';
import ScoreCard, { MiniScoreBar } from '../components/ScoreCard';
import { ScoreBreakdownChart, SkillsAnalysis, ATSFindings, SHAPChart } from '../components/SkillChart';
import {
  Loader2, ArrowLeft, FileText, Briefcase, Clock,
  Lightbulb, AlertTriangle, CheckCircle, Info,
  TrendingUp, Shield, Brain, Search,
} from 'lucide-react';

const SCORE_COLORS = ['#818cf8', '#38bdf8', '#34d399', '#fbbf24', '#f97316', '#a78bfa'];

const SEVERITY_CONFIG = {
  high: { icon: AlertTriangle, class: 'severity-high', bg: 'bg-red-500/5 border-red-500/20' },
  medium: { icon: Info, class: 'severity-medium', bg: 'bg-amber-500/5 border-amber-500/20' },
  low: { icon: CheckCircle, class: 'severity-low', bg: 'bg-blue-500/5 border-blue-500/20' },
};

export default function Results() {
  const { id } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadAnalysis();
  }, [id]);

  const loadAnalysis = async () => {
    try {
      const res = await analysisAPI.get(id);
      setAnalysis(res.data);
    } catch (error) {
      console.error('Failed to load analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-24 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-10 h-10 text-primary-400 animate-spin mx-auto" />
          <p className="text-dark-400 mt-4">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className="min-h-screen pt-24 flex items-center justify-center">
        <div className="text-center">
          <p className="text-dark-400 mb-4">Analysis not found</p>
          <Link to="/analyze" className="btn-primary">New Analysis</Link>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: TrendingUp },
    { id: 'skills', label: 'Skills', icon: Brain },
    { id: 'ats', label: 'ATS', icon: Shield },
    { id: 'explain', label: 'Explain', icon: Search },
    { id: 'suggestions', label: 'Improve', icon: Lightbulb },
  ];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-8">
          <div>
            <Link to="/history" className="text-sm text-dark-400 hover:text-primary-400 flex items-center gap-1 mb-2 transition-colors">
              <ArrowLeft className="w-3 h-3" /> Back to History
            </Link>
            <h1 className="text-2xl md:text-3xl font-bold font-display text-white">Analysis Results</h1>
            <div className="flex items-center gap-4 mt-2 text-sm text-dark-400">
              {analysis.resume_name && (
                <span className="flex items-center gap-1">
                  <FileText className="w-3.5 h-3.5" /> {analysis.resume_name}
                </span>
              )}
              {analysis.job_title && (
                <span className="flex items-center gap-1">
                  <Briefcase className="w-3.5 h-3.5" /> {analysis.job_title}
                </span>
              )}
              <span className="flex items-center gap-1">
                <Clock className="w-3.5 h-3.5" /> {new Date(analysis.created_at).toLocaleString()}
              </span>
            </div>
          </div>
          <Link to="/analyze" className="btn-secondary flex items-center gap-2 text-sm">
            <Search className="w-4 h-4" /> New Analysis
          </Link>
        </div>

        {/* Score Card Hero */}
        <div className="glass-card p-8 mb-6 flex flex-col md:flex-row items-center gap-8 animate-slide-up">
          <ScoreCard score={analysis.match_score} classification={analysis.classification} />

          <div className="flex-1 w-full space-y-3">
            <h3 className="text-lg font-semibold text-white mb-4">Score Breakdown</h3>
            {analysis.score_breakdown?.map((item, i) => (
              <MiniScoreBar
                key={i}
                label={item.component}
                score={item.score}
                weight={item.weight}
                color={SCORE_COLORS[i % SCORE_COLORS.length]}
              />
            ))}
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-1 mb-6 overflow-x-auto pb-2">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all
                  ${activeTab === tab.id
                    ? 'bg-primary-500/15 text-primary-400 shadow-sm'
                    : 'text-dark-400 hover:text-white hover:bg-dark-800/50'
                  }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
                {tab.id === 'suggestions' && analysis.suggestions?.length > 0 && (
                  <span className="w-5 h-5 rounded-full bg-primary-500/20 text-primary-400 text-xs flex items-center justify-center">
                    {analysis.suggestions.length}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="animate-fade-in" key={activeTab}>
          {activeTab === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ScoreBreakdownChart breakdown={analysis.score_breakdown || []} />

              <div className="glass-card p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Quick Summary</h3>
                <div className="space-y-4">
                  <div className="flex items-start gap-3 p-3 rounded-xl bg-dark-800/30">
                    <Brain className="w-5 h-5 text-primary-400 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-white">Classification</p>
                      <p className="text-sm text-dark-400">
                        {analysis.classification}
                        {analysis.classification_confidence &&
                          ` (${(analysis.classification_confidence * 100).toFixed(0)}% confidence)`
                        }
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-xl bg-dark-800/30">
                    <CheckCircle className="w-5 h-5 text-emerald-400 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-white">Matched Skills</p>
                      <p className="text-sm text-dark-400">{analysis.matched_skills?.length || 0} skills match the JD</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-xl bg-dark-800/30">
                    <AlertTriangle className="w-5 h-5 text-amber-400 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-white">Missing Skills</p>
                      <p className="text-sm text-dark-400">{analysis.missing_skills?.length || 0} required skills not found</p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3 p-3 rounded-xl bg-dark-800/30">
                    <Shield className="w-5 h-5 text-blue-400 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-white">ATS Compatibility</p>
                      <p className="text-sm text-dark-400">{analysis.ats_score?.toFixed(0)}% compatible with ATS systems</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'skills' && (
            <SkillsAnalysis
              matchedSkills={analysis.matched_skills || []}
              missingSkills={analysis.missing_skills || []}
            />
          )}

          {activeTab === 'ats' && (
            <ATSFindings
              findings={analysis.ats_findings || []}
              atsScore={analysis.ats_score || 0}
            />
          )}

          {activeTab === 'explain' && (
            <SHAPChart explanations={analysis.shap_explanation || []} />
          )}

          {activeTab === 'suggestions' && (
            <div className="glass-card p-6">
              <div className="flex items-center gap-3 mb-5">
                <div className="w-10 h-10 rounded-xl bg-amber-500/15 flex items-center justify-center">
                  <Lightbulb className="w-5 h-5 text-amber-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Improvement Suggestions</h3>
                  <p className="text-xs text-dark-400">Evidence-based recommendations to strengthen your resume</p>
                </div>
              </div>

              {analysis.suggestions?.length > 0 ? (
                <div className="space-y-3">
                  {analysis.suggestions.map((s, i) => {
                    const config = SEVERITY_CONFIG[s.severity] || SEVERITY_CONFIG.low;
                    const Icon = config.icon;
                    return (
                      <div key={i} className={`p-4 rounded-xl border ${config.bg}`}>
                        <div className="flex items-start gap-3">
                          <Icon className="w-4 h-4 mt-0.5 flex-shrink-0" style={{
                            color: s.severity === 'high' ? '#f87171' : s.severity === 'medium' ? '#fbbf24' : '#60a5fa',
                          }} />
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className={config.class}>{s.severity.toUpperCase()}</span>
                              <span className="text-xs text-dark-500 px-2 py-0.5 rounded bg-dark-800/50">{s.category}</span>
                            </div>
                            <p className="text-sm text-dark-200">{s.suggestion}</p>
                            {s.evidence && (
                              <p className="text-xs text-dark-400 mt-1.5 italic">Evidence: {s.evidence}</p>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-10 text-dark-400">
                  <CheckCircle className="w-10 h-10 mx-auto mb-3 text-emerald-400" />
                  <p>No major improvements needed — your resume looks great!</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
