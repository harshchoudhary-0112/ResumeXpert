/**
 * Home — premium landing page with hero section,
 * features grid, and call-to-action.
 */

import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Sparkles, FileSearch, Brain, Shield, BarChart3, Lightbulb,
  Zap, Target, ArrowRight, CheckCircle2,
} from 'lucide-react';

const FEATURES = [
  {
    icon: FileSearch,
    title: 'Smart Resume Parsing',
    desc: 'Extracts skills, experience, education, and projects from PDF/DOCX with intelligent section detection.',
    color: '#818cf8',
  },
  {
    icon: Brain,
    title: 'NLP & Semantic Matching',
    desc: 'Goes beyond keywords — uses Sentence-Transformers to understand the meaning behind your resume and the JD.',
    color: '#38bdf8',
  },
  {
    icon: Target,
    title: 'Skill Gap Analysis',
    desc: 'Identifies exactly which required and preferred skills you have and which ones are missing.',
    color: '#34d399',
  },
  {
    icon: Shield,
    title: 'ATS Compatibility',
    desc: 'Checks for 12+ common issues that cause ATS systems to reject or misparse your resume.',
    color: '#f59e0b',
  },
  {
    icon: BarChart3,
    title: 'ML Classification & SHAP',
    desc: 'XGBoost-powered classification with SHAP explanations showing exactly what drives the score.',
    color: '#a78bfa',
  },
  {
    icon: Lightbulb,
    title: 'Actionable Suggestions',
    desc: 'Evidence-based improvement recommendations grounded in your actual resume — never fabricated.',
    color: '#f472b6',
  },
];

const STATS = [
  { value: '300+', label: 'Skills in Taxonomy' },
  { value: '12+', label: 'ATS Checks' },
  { value: '6', label: 'Score Components' },
  { value: '3', label: 'ML Models' },
];

export default function Home() {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen">
      {/* ── Hero Section ──────────────────────────────────── */}
      <section className="relative pt-32 pb-20 px-4 overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 mesh-gradient" />
        <div className="absolute top-20 left-1/4 w-72 h-72 bg-primary-500/10 rounded-full blur-[120px] animate-pulse-slow" />
        <div className="absolute bottom-10 right-1/4 w-96 h-96 bg-accent-500/8 rounded-full blur-[150px] animate-pulse-slow" />

        <div className="max-w-5xl mx-auto text-center relative z-10">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 mb-8 animate-fade-in">
            <Zap className="w-4 h-4 text-primary-400" />
            <span className="text-sm font-medium text-primary-300">AI-Powered Resume Intelligence</span>
          </div>

          {/* Headline */}
          <h1 className="text-5xl md:text-7xl font-bold font-display leading-tight mb-6 animate-slide-up">
            <span className="text-white">Analyze. Match.</span>
            <br />
            <span className="gradient-text">Optimize.</span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg md:text-xl text-dark-300 max-w-2xl mx-auto mb-10 leading-relaxed animate-slide-up" style={{ animationDelay: '0.1s' }}>
            ResumeXpert uses NLP, semantic similarity, and explainable ML to analyze your resume
            against any job description — revealing skill gaps, ATS issues, and exactly how to improve.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <Link
              to={isAuthenticated ? '/analyze' : '/register'}
              className="btn-primary text-lg !px-8 !py-4 flex items-center gap-2 group"
            >
              <Sparkles className="w-5 h-5" />
              {isAuthenticated ? 'Analyze Resume' : 'Get Started Free'}
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            {!isAuthenticated && (
              <Link to="/login" className="btn-secondary text-lg !px-8 !py-4">
                Sign In
              </Link>
            )}
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-16 animate-slide-up" style={{ animationDelay: '0.3s' }}>
            {STATS.map((stat, i) => (
              <div key={i} className="glass-card p-4 text-center">
                <div className="text-3xl font-bold font-display gradient-text">{stat.value}</div>
                <div className="text-sm text-dark-400 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features Grid ─────────────────────────────────── */}
      <section className="py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-bold font-display text-white mb-4">
              Everything You Need to
              <span className="gradient-text"> Land the Interview</span>
            </h2>
            <p className="text-dark-400 max-w-xl mx-auto">
              A comprehensive pipeline from resume parsing to explainable scoring and evidence-based improvements.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <div
                  key={i}
                  className="glass-card-hover p-6 group"
                  style={{ animationDelay: `${i * 0.1}s` }}
                >
                  <div
                    className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-transform group-hover:scale-110"
                    style={{ backgroundColor: `${feature.color}15`, border: `1px solid ${feature.color}25` }}
                  >
                    <Icon className="w-6 h-6" style={{ color: feature.color }} />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-sm text-dark-400 leading-relaxed">{feature.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── How It Works ──────────────────────────────────── */}
      <section className="py-20 px-4 border-t border-dark-800/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold font-display text-white text-center mb-14">
            How It Works
          </h2>
          <div className="space-y-6">
            {[
              { step: '01', title: 'Upload Your Resume', desc: 'Drop a PDF or DOCX — we extract and parse everything automatically.' },
              { step: '02', title: 'Paste the Job Description', desc: 'Enter the target JD — we extract required skills, experience, and education.' },
              { step: '03', title: 'Get Instant Analysis', desc: 'View your match score, skill gaps, ATS findings, and ML-powered classification.' },
              { step: '04', title: 'Improve & Reanalyze', desc: 'Follow evidence-based suggestions to strengthen your resume and boost your score.' },
            ].map((item, i) => (
              <div key={i} className="glass-card-hover p-6 flex items-start gap-5">
                <div className="text-3xl font-bold font-display text-primary-500/30">{item.step}</div>
                <div>
                  <h3 className="text-lg font-semibold text-white mb-1">{item.title}</h3>
                  <p className="text-sm text-dark-400">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link
              to={isAuthenticated ? '/analyze' : '/register'}
              className="btn-primary text-lg !px-8 !py-4 inline-flex items-center gap-2"
            >
              Start Analyzing
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ────────────────────────────────────────── */}
      <footer className="border-t border-dark-800/50 py-8 px-4">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-primary-400" />
            <span className="font-display font-bold text-white">ResumeXpert</span>
          </div>
          <p className="text-sm text-dark-500">
            AI-powered decision-support tool. Not a replacement for human hiring decisions.
          </p>
        </div>
      </footer>
    </div>
  );
}
