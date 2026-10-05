/**
 * Dashboard — user stats, score distribution, recent analyses,
 * and top missing skills overview.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { analysisAPI } from '../services/api';
import { ScoreDistributionChart } from '../components/SkillChart';
import {
  BarChart3, FileText, Briefcase, TrendingUp,
  Clock, ArrowRight, Search, Loader2, Trophy,
} from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const res = await analysisAPI.dashboard();
      setStats(res.data);
    } catch (error) {
      console.error('Failed to load dashboard:', error);
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

  const statCards = [
    {
      label: 'Total Analyses',
      value: stats?.total_analyses || 0,
      icon: BarChart3,
      color: '#818cf8',
    },
    {
      label: 'Resumes Uploaded',
      value: stats?.total_resumes || 0,
      icon: FileText,
      color: '#38bdf8',
    },
    {
      label: 'Job Descriptions',
      value: stats?.total_jobs || 0,
      icon: Briefcase,
      color: '#34d399',
    },
    {
      label: 'Average Score',
      value: `${(stats?.average_score || 0).toFixed(1)}%`,
      icon: TrendingUp,
      color: '#f59e0b',
    },
  ];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold font-display text-white">
              Welcome back, <span className="gradient-text">{user?.name?.split(' ')[0]}</span>
            </h1>
            <p className="text-dark-400 mt-1">Here's an overview of your resume analysis activity.</p>
          </div>
          <Link to="/analyze" className="btn-primary flex items-center gap-2">
            <Search className="w-4 h-4" />
            New Analysis
          </Link>
        </div>

        {/* Stat Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {statCards.map((card, i) => {
            const Icon = card.icon;
            return (
              <div key={i} className="glass-card-hover p-5 animate-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
                <div className="flex items-center justify-between mb-3">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center"
                    style={{ backgroundColor: `${card.color}15`, border: `1px solid ${card.color}25` }}
                  >
                    <Icon className="w-5 h-5" style={{ color: card.color }} />
                  </div>
                  {card.label === 'Average Score' && stats?.highest_score > 0 && (
                    <div className="flex items-center gap-1 text-xs text-amber-400">
                      <Trophy className="w-3 h-3" />
                      Best: {stats.highest_score.toFixed(0)}%
                    </div>
                  )}
                </div>
                <div className="text-2xl font-bold font-display text-white">{card.value}</div>
                <div className="text-sm text-dark-400 mt-0.5">{card.label}</div>
              </div>
            );
          })}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Score Distribution */}
          <ScoreDistributionChart distribution={stats?.score_distribution || {}} />

          {/* Top Missing Skills */}
          <div className="glass-card p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Top Missing Skills</h3>
            {stats?.top_missing_skills?.length > 0 ? (
              <div className="space-y-3">
                {stats.top_missing_skills.slice(0, 8).map((item, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <span className="text-sm text-dark-200">{item.skill}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-dark-700/50 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-red-400/60 rounded-full"
                          style={{ width: `${Math.min(100, (item.count / (stats.total_analyses || 1)) * 100)}%` }}
                        />
                      </div>
                      <span className="text-xs text-dark-400 w-6 text-right">{item.count}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-48 text-dark-400 text-sm">
                Run your first analysis to see skill gaps
              </div>
            )}
          </div>
        </div>

        {/* Recent Analyses */}
        <div className="glass-card p-6 mt-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-white">Recent Analyses</h3>
            {stats?.recent_analyses?.length > 0 && (
              <Link to="/history" className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1">
                View All <ArrowRight className="w-3 h-3" />
              </Link>
            )}
          </div>

          {stats?.recent_analyses?.length > 0 ? (
            <div className="space-y-3">
              {stats.recent_analyses.map((analysis, i) => (
                <Link
                  key={i}
                  to={`/results/${analysis.id}`}
                  className="flex items-center justify-between p-4 rounded-xl bg-dark-800/30 border border-dark-700/30 hover:border-primary-500/20 transition-all group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-primary-500/10 flex items-center justify-center">
                      <FileText className="w-5 h-5 text-primary-400" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white group-hover:text-primary-300 transition-colors">
                        {analysis.resume_filename || 'Resume'} → {analysis.job_title || 'Job'}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <Clock className="w-3 h-3 text-dark-500" />
                        <span className="text-xs text-dark-500">
                          {new Date(analysis.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-lg font-bold ${
                      analysis.match_score >= 75 ? 'text-emerald-400' :
                      analysis.match_score >= 50 ? 'text-amber-400' :
                      analysis.match_score >= 30 ? 'text-orange-400' : 'text-red-400'
                    }`}>
                      {analysis.match_score.toFixed(0)}%
                    </span>
                    <ArrowRight className="w-4 h-4 text-dark-500 group-hover:text-primary-400 transition-colors" />
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-36 text-center">
              <p className="text-dark-400 text-sm mb-4">No analyses yet. Start your first one!</p>
              <Link to="/analyze" className="btn-primary text-sm !px-5 !py-2 flex items-center gap-2">
                <Search className="w-4 h-4" /> Analyze Resume
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
