/**
 * Register page — glassmorphism card with strong password validation
 * and OTP email verification flow.
 */

import { useState, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import {
  Sparkles, User, Mail, Lock, Loader2, ArrowRight,
  Eye, EyeOff, Check, X, ShieldCheck,
} from 'lucide-react';
import toast from 'react-hot-toast';

/* ── Password policy checks ─────────────────────────────────── */
const PASSWORD_RULES = [
  { id: 'length',    label: 'At least 8 characters',              test: (p) => p.length >= 8 },
  { id: 'uppercase', label: 'One uppercase letter (A-Z)',          test: (p) => /[A-Z]/.test(p) },
  { id: 'lowercase', label: 'One lowercase letter (a-z)',          test: (p) => /[a-z]/.test(p) },
  { id: 'number',    label: 'One number (0-9)',                    test: (p) => /\d/.test(p) },
  { id: 'special',   label: 'One special character (!@#$%…)',      test: (p) => /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>/?`~]/.test(p) },
];

const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

/* ── Strength meter ─────────────────────────────────────────── */
function PasswordStrengthMeter({ password }) {
  const passed = PASSWORD_RULES.filter((r) => r.test(password)).length;
  const pct = (passed / PASSWORD_RULES.length) * 100;

  const color =
    pct <= 20  ? 'bg-red-500' :
    pct <= 40  ? 'bg-orange-500' :
    pct <= 60  ? 'bg-yellow-500' :
    pct <= 80  ? 'bg-lime-400' :
                 'bg-emerald-500';

  const label =
    pct <= 20  ? 'Very Weak' :
    pct <= 40  ? 'Weak' :
    pct <= 60  ? 'Fair' :
    pct <= 80  ? 'Good' :
                 'Strong';

  if (!password) return null;

  return (
    <div className="mt-2">
      {/* bar */}
      <div className="h-1.5 rounded-full bg-dark-800 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-xs mt-1.5 text-dark-400">
        Strength: <span className={`font-semibold ${color.replace('bg-', 'text-')}`}>{label}</span>
      </p>
    </div>
  );
}

/* ── Component ──────────────────────────────────────────────── */
export default function Register() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showRules, setShowRules] = useState(false);
  const navigate = useNavigate();

  /* derived */
  const allRulesPassed = useMemo(
    () => PASSWORD_RULES.every((r) => r.test(password)),
    [password],
  );
  const emailValid = useMemo(() => EMAIL_REGEX.test(email), [email]);
  const passwordsMatch = password && confirmPassword && password === confirmPassword;

  const canSubmit =
    name.trim().length >= 2 &&
    emailValid &&
    allRulesPassed &&
    passwordsMatch &&
    !loading;

  /* submit */
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!emailValid) {
      toast.error('Please enter a valid email address');
      return;
    }
    if (!allRulesPassed) {
      toast.error('Password does not meet the security requirements');
      return;
    }
    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await authAPI.register({
        name: name.trim(),
        email: email.trim().toLowerCase(),
        password,
        confirm_password: confirmPassword,
      });
      toast.success('Verification code sent to your email!');
      navigate('/verify-email', { state: { email: email.trim().toLowerCase() } });
    } catch (error) {
      const detail = error.response?.data?.detail;
      if (Array.isArray(detail)) {
        toast.error(detail[0]?.msg || 'Registration failed');
      } else {
        toast.error(detail || 'Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-16 pb-12">
      <div className="absolute inset-0 mesh-gradient" />
      <div className="absolute bottom-20 right-1/3 w-80 h-80 bg-accent-500/10 rounded-full blur-[120px]" />

      <div className="w-full max-w-md relative z-10 animate-slide-up">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg shadow-primary-500/25">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold font-display text-white">
              Resume<span className="text-primary-400">Xpert</span>
            </span>
          </Link>
          <h1 className="text-2xl font-bold font-display text-white">Create your account</h1>
          <p className="text-dark-400 mt-1">Start optimizing your resume today</p>
        </div>

        {/* Form */}
        <div className="glass-card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">Full Name</label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
                <input
                  id="register-name"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input-field !pl-11"
                  placeholder="Enter Full Name"
                  required
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">Email</label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
                <input
                  id="register-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`input-field !pl-11 ${email && !emailValid ? '!border-red-500/50' : ''}`}
                  placeholder="you@example.com"
                  required
                />
              </div>
              {email && !emailValid && (
                <p className="text-xs text-red-400 mt-1.5">Please enter a valid email address</p>
              )}
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
                <input
                  id="register-password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setShowRules(true); }}
                  onFocus={() => setShowRules(true)}
                  className="input-field !pl-11 !pr-11"
                  placeholder="Min. 8 characters"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-dark-400 hover:text-dark-200 transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>

              <PasswordStrengthMeter password={password} />

              {/* Password rules checklist */}
              {showRules && password && (
                <div className="mt-3 space-y-1.5 p-3 rounded-lg bg-dark-900/50 border border-dark-700/50">
                  {PASSWORD_RULES.map((rule) => {
                    const ok = rule.test(password);
                    return (
                      <div key={rule.id} className="flex items-center gap-2 text-xs">
                        {ok ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        ) : (
                          <X className="w-3.5 h-3.5 text-dark-500 flex-shrink-0" />
                        )}
                        <span className={ok ? 'text-emerald-400' : 'text-dark-500'}>
                          {rule.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-dark-300 mb-2">Confirm Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
                <input
                  id="register-confirm-password"
                  type={showConfirm ? 'text' : 'password'}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={`input-field !pl-11 !pr-11 ${
                    confirmPassword && !passwordsMatch ? '!border-red-500/50' : ''
                  } ${passwordsMatch ? '!border-emerald-500/50' : ''}`}
                  placeholder="••••••••"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirm(!showConfirm)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-dark-400 hover:text-dark-200 transition-colors"
                  tabIndex={-1}
                >
                  {showConfirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {confirmPassword && !passwordsMatch && (
                <p className="text-xs text-red-400 mt-1.5">Passwords do not match</p>
              )}
              {passwordsMatch && (
                <p className="text-xs text-emerald-400 mt-1.5 flex items-center gap-1">
                  <Check className="w-3 h-3" /> Passwords match
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={!canSubmit}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  Create Account
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-dark-400">
              Already have an account?{' '}
              <Link to="/login" className="text-primary-400 font-medium hover:text-primary-300 transition-colors">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
