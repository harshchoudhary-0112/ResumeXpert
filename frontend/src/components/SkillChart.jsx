/**
 * SkillChart — visualizes matched vs missing skills using Recharts
 * radar/bar charts and skill tag lists.
 */

import {
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell, PieChart, Pie,
} from 'recharts';
import { Check, X, AlertTriangle } from 'lucide-react';

const CATEGORY_COLORS = {
  programming_languages: '#818cf8',
  web_frontend: '#38bdf8',
  web_backend: '#34d399',
  databases: '#fbbf24',
  cloud_devops: '#f97316',
  data_science_ml: '#a78bfa',
  mobile_development: '#f472b6',
  testing_qa: '#2dd4bf',
  tools_practices: '#94a3b8',
  security: '#ef4444',
  soft_skills: '#14b8a6',
  other: '#64748b',
};

const CATEGORY_LABELS = {
  programming_languages: 'Languages',
  web_frontend: 'Frontend',
  web_backend: 'Backend',
  databases: 'Databases',
  cloud_devops: 'Cloud & DevOps',
  data_science_ml: 'Data/ML',
  mobile_development: 'Mobile',
  testing_qa: 'Testing',
  tools_practices: 'Tools',
  security: 'Security',
  soft_skills: 'Soft Skills',
  other: 'Other',
};

/**
 * Score breakdown bar chart
 */
export function ScoreBreakdownChart({ breakdown = [] }) {
  const data = breakdown.map(item => ({
    name: item.component.replace(' Match', '').replace(' Similarity', '').replace(' Compatibility', '').replace(' Relevance', ''),
    score: item.score,
    weighted: item.weighted_score,
  }));

  const barColors = ['#818cf8', '#38bdf8', '#34d399', '#fbbf24', '#f97316', '#a78bfa'];

  return (
    <div className="glass-card p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Score Breakdown</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,116,139,0.15)" horizontal={false} />
          <XAxis type="number" domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} />
          <YAxis dataKey="name" type="category" tick={{ fill: '#cbd5e1', fontSize: 13 }} width={90} axisLine={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid rgba(100,116,139,0.3)',
              borderRadius: '12px',
              color: '#e2e8f0',
            }}
            formatter={(value) => [`${value.toFixed(1)}`, 'Score']}
          />
          <Bar dataKey="score" radius={[0, 6, 6, 0]} barSize={20}>
            {data.map((_, index) => (
              <Cell key={index} fill={barColors[index % barColors.length]} fillOpacity={0.85} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * Matched vs Missing skills visual
 */
export function SkillsAnalysis({ matchedSkills = [], missingSkills = [] }) {
  return (
    <div className="glass-card p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Skills Analysis</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Matched Skills */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-6 h-6 rounded-full bg-emerald-500/20 flex items-center justify-center">
              <Check className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <span className="text-sm font-semibold text-emerald-400">
              Matched Skills ({matchedSkills.length})
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {matchedSkills.length > 0 ? matchedSkills.map((skill, i) => (
              <span
                key={i}
                className="px-3 py-1.5 text-xs font-medium rounded-lg border transition-all hover:scale-105"
                style={{
                  backgroundColor: `${CATEGORY_COLORS[skill.category] || CATEGORY_COLORS.other}15`,
                  borderColor: `${CATEGORY_COLORS[skill.category] || CATEGORY_COLORS.other}30`,
                  color: CATEGORY_COLORS[skill.category] || CATEGORY_COLORS.other,
                }}
              >
                {skill.skill}
              </span>
            )) : (
              <span className="text-dark-400 text-sm">No matching skills found</span>
            )}
          </div>
        </div>

        {/* Missing Skills */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-6 h-6 rounded-full bg-red-500/20 flex items-center justify-center">
              <X className="w-3.5 h-3.5 text-red-400" />
            </div>
            <span className="text-sm font-semibold text-red-400">
              Missing Skills ({missingSkills.length})
            </span>
          </div>
          <div className="flex flex-wrap gap-2">
            {missingSkills.length > 0 ? missingSkills.map((skill, i) => (
              <span
                key={i}
                className="px-3 py-1.5 text-xs font-medium rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 transition-all hover:scale-105"
              >
                {skill}
              </span>
            )) : (
              <span className="text-dark-400 text-sm">No missing skills — great match!</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * ATS Findings display
 */
export function ATSFindings({ findings = [], atsScore = 0 }) {
  const severityIcon = {
    critical: <X className="w-4 h-4 text-red-400" />,
    warning: <AlertTriangle className="w-4 h-4 text-amber-400" />,
    info: <Check className="w-4 h-4 text-blue-400" />,
  };

  const severityBg = {
    critical: 'border-red-500/20 bg-red-500/5',
    warning: 'border-amber-500/20 bg-amber-500/5',
    info: 'border-blue-500/20 bg-blue-500/5',
  };

  return (
    <div className="glass-card p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">ATS Compatibility</h3>
        <span className={`text-2xl font-bold ${atsScore >= 80 ? 'text-emerald-400' : atsScore >= 60 ? 'text-amber-400' : 'text-red-400'}`}>
          {atsScore.toFixed(0)}%
        </span>
      </div>
      <div className="space-y-2">
        {findings.map((finding, i) => (
          <div
            key={i}
            className={`flex items-start gap-3 p-3 rounded-xl border ${severityBg[finding.severity] || severityBg.info}`}
          >
            <div className="mt-0.5">{severityIcon[finding.severity] || severityIcon.info}</div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-dark-200">{finding.issue}</p>
              <p className="text-xs text-dark-400 mt-0.5">{finding.recommendation}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

/**
 * SHAP Explanation chart
 */
export function SHAPChart({ explanations = [] }) {
  const data = explanations.slice(0, 8).map(item => ({
    name: item.feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
    contribution: item.contribution,
    value: item.value,
  }));

  return (
    <div className="glass-card p-6">
      <h3 className="text-lg font-semibold text-white mb-1">Feature Contributions</h3>
      <p className="text-xs text-dark-400 mb-4">What factors influenced the classification</p>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} layout="vertical" margin={{ left: 30, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,116,139,0.15)" horizontal={false} />
          <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 12 }} axisLine={false} />
          <YAxis dataKey="name" type="category" tick={{ fill: '#cbd5e1', fontSize: 11 }} width={120} axisLine={false} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid rgba(100,116,139,0.3)',
              borderRadius: '12px',
              color: '#e2e8f0',
            }}
            formatter={(value) => [value.toFixed(4), 'Contribution']}
          />
          <Bar dataKey="contribution" radius={[0, 4, 4, 0]} barSize={16}>
            {data.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.contribution >= 0 ? '#34d399' : '#f87171'}
                fillOpacity={0.8}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

/**
 * Score distribution pie chart for the dashboard
 */
export function ScoreDistributionChart({ distribution = {} }) {
  const data = Object.entries(distribution)
    .filter(([_, count]) => count > 0)
    .map(([range, count]) => ({
      name: range,
      value: count,
    }));

  const COLORS = ['#ef4444', '#f97316', '#fbbf24', '#34d399', '#10b981'];

  if (data.length === 0) {
    return (
      <div className="glass-card p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Score Distribution</h3>
        <div className="flex items-center justify-center h-48 text-dark-400 text-sm">
          No analyses yet
        </div>
      </div>
    );
  }

  return (
    <div className="glass-card p-6">
      <h3 className="text-lg font-semibold text-white mb-4">Score Distribution</h3>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={50}
            outerRadius={80}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} fillOpacity={0.85} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#1e293b',
              border: '1px solid rgba(100,116,139,0.3)',
              borderRadius: '12px',
              color: '#e2e8f0',
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap justify-center gap-3 mt-2">
        {data.map((entry, i) => (
          <div key={i} className="flex items-center gap-1.5 text-xs text-dark-300">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
            {entry.name}: {entry.value}
          </div>
        ))}
      </div>
    </div>
  );
}
