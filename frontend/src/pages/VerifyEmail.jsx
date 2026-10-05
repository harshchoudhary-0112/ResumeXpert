/**
 * VerifyEmail page — 6-digit OTP input with auto-focus,
 * resend cooldown timer, and attempt tracking.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authAPI } from '../services/api';
import {
  Sparkles, ShieldCheck, Loader2, ArrowRight,
  MailCheck, RefreshCw, ArrowLeft,
} from 'lucide-react';
import toast from 'react-hot-toast';

const OTP_LENGTH = 6;
const RESEND_COOLDOWN = 60; // seconds

export default function VerifyEmail() {
  const location = useLocation();
  const navigate = useNavigate();
  const { login } = useAuth();

  const email = location.state?.email;

  const [otp, setOtp] = useState(Array(OTP_LENGTH).fill(''));
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const [cooldown, setCooldown] = useState(RESEND_COOLDOWN);
  const inputRefs = useRef([]);

  // Redirect if no email in state (user navigated directly)
  useEffect(() => {
    if (!email) {
      navigate('/register', { replace: true });
    }
  }, [email, navigate]);

  // Countdown timer for resend cooldown
  useEffect(() => {
    if (cooldown <= 0) return;
    const timer = setInterval(() => {
      setCooldown((prev) => (prev <= 1 ? 0 : prev - 1));
    }, 1000);
    return () => clearInterval(timer);
  }, [cooldown]);

  // Auto-focus first input on mount
  useEffect(() => {
    inputRefs.current[0]?.focus();
  }, []);

  /* ── Input handlers ─────────────────────────────────────── */
  const handleChange = (index, value) => {
    // Only allow digits
    if (value && !/^\d$/.test(value)) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto-advance to next input
    if (value && index < OTP_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-submit when all digits filled
    if (value && index === OTP_LENGTH - 1 && newOtp.every((d) => d)) {
      handleVerify(newOtp.join(''));
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === 'ArrowRight' && index < OTP_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const text = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, OTP_LENGTH);
    if (!text) return;

    const newOtp = [...otp];
    for (let i = 0; i < text.length; i++) {
      newOtp[i] = text[i];
    }
    setOtp(newOtp);

    // Focus the next empty or last input
    const nextEmpty = newOtp.findIndex((d) => !d);
    inputRefs.current[nextEmpty >= 0 ? nextEmpty : OTP_LENGTH - 1]?.focus();

    // Auto-submit if complete
    if (newOtp.every((d) => d)) {
      handleVerify(newOtp.join(''));
    }
  };

  /* ── Verify OTP ─────────────────────────────────────────── */
  const handleVerify = useCallback(async (code) => {
    if (loading) return;
    setLoading(true);

    try {
      const res = await authAPI.verifyOtp({ email, otp: code });
      const { access_token } = res.data;

      // Store token and load profile
      localStorage.setItem('resumexpert_token', access_token);
      // Fetch profile to populate auth state
      const profileRes = await authAPI.getProfile();
      localStorage.setItem('resumexpert_user', JSON.stringify(profileRes.data));

      toast.success('Email verified! Welcome to ResumeXpert!');
      // Force full reload to re-initialize AuthContext with new token
      window.location.href = '/dashboard';
    } catch (error) {
      const detail = error.response?.data?.detail || 'Verification failed';
      toast.error(detail);
      // Clear OTP fields on error
      setOtp(Array(OTP_LENGTH).fill(''));
      inputRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  }, [email, loading]);

  /* ── Resend OTP ─────────────────────────────────────────── */
  const handleResend = async () => {
    if (cooldown > 0 || resending) return;
    setResending(true);

    try {
      await authAPI.resendOtp({ email });
      toast.success('A new verification code has been sent!');
      setCooldown(RESEND_COOLDOWN);
      setOtp(Array(OTP_LENGTH).fill(''));
      inputRefs.current[0]?.focus();
    } catch (error) {
      const detail = error.response?.data?.detail || 'Failed to resend code';
      toast.error(detail);
    } finally {
      setResending(false);
    }
  };

  /* ── Manual submit ──────────────────────────────────────── */
  const handleSubmit = (e) => {
    e.preventDefault();
    const code = otp.join('');
    if (code.length !== OTP_LENGTH) {
      toast.error('Please enter the complete 6-digit code');
      return;
    }
    handleVerify(code);
  };

  if (!email) return null;

  const maskedEmail = email.replace(/(.{2})(.*)(@.*)/, (_, a, b, c) =>
    a + '•'.repeat(Math.min(b.length, 5)) + c
  );

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-16 pb-12">
      <div className="absolute inset-0 mesh-gradient" />
      <div className="absolute top-32 left-1/4 w-72 h-72 bg-emerald-500/8 rounded-full blur-[120px]" />
      <div className="absolute bottom-20 right-1/3 w-80 h-80 bg-primary-500/8 rounded-full blur-[120px]" />

      <div className="w-full max-w-md relative z-10 animate-slide-up">
        {/* Header */}
        <div className="text-center mb-8">
          <Link to="/" className="inline-flex items-center gap-2 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center shadow-lg shadow-primary-500/25">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold font-display text-white">
              Resume<span className="text-primary-400">Xpert</span>
            </span>
          </Link>

          {/* Email icon with pulse */}
          <div className="mx-auto w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500/20 to-primary-500/20 border border-emerald-500/20 flex items-center justify-center mb-4">
            <MailCheck className="w-8 h-8 text-emerald-400" />
          </div>

          <h1 className="text-2xl font-bold font-display text-white">Verify your email</h1>
          <p className="text-dark-400 mt-2 text-sm">
            We've sent a 6-digit code to{' '}
            <span className="text-primary-400 font-medium">{maskedEmail}</span>
          </p>
        </div>

        {/* OTP Card */}
        <div className="glass-card p-8">
          <form onSubmit={handleSubmit}>
            {/* OTP Input Grid */}
            <div className="flex justify-center gap-3 mb-6">
              {otp.map((digit, idx) => (
                <input
                  key={idx}
                  id={`otp-${idx}`}
                  ref={(el) => (inputRefs.current[idx] = el)}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleChange(idx, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(idx, e)}
                  onPaste={idx === 0 ? handlePaste : undefined}
                  disabled={loading}
                  className={`
                    w-12 h-14 text-center text-xl font-bold font-mono
                    rounded-xl border transition-all duration-200
                    bg-dark-800/50 text-white
                    focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500
                    ${digit
                      ? 'border-primary-500/50 shadow-lg shadow-primary-500/10'
                      : 'border-dark-600 hover:border-dark-500'
                    }
                    disabled:opacity-50 disabled:cursor-not-allowed
                  `}
                  autoComplete="one-time-code"
                />
              ))}
            </div>

            {/* Verify Button */}
            <button
              type="submit"
              disabled={loading || otp.some((d) => !d)}
              className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  Verify Email
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Resend Section */}
          <div className="mt-6 text-center">
            <p className="text-sm text-dark-400 mb-2">Didn't receive the code?</p>
            {cooldown > 0 ? (
              <p className="text-sm text-dark-500">
                Resend available in{' '}
                <span className="text-primary-400 font-mono font-semibold">
                  {Math.floor(cooldown / 60)}:{(cooldown % 60).toString().padStart(2, '0')}
                </span>
              </p>
            ) : (
              <button
                onClick={handleResend}
                disabled={resending}
                className="inline-flex items-center gap-1.5 text-sm text-primary-400 font-medium hover:text-primary-300 transition-colors disabled:opacity-50"
              >
                {resending ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <RefreshCw className="w-3.5 h-3.5" />
                )}
                Resend Code
              </button>
            )}
          </div>

          {/* Back link */}
          <div className="mt-5 pt-5 border-t border-dark-700/50 text-center">
            <Link
              to="/register"
              className="inline-flex items-center gap-1.5 text-sm text-dark-400 hover:text-dark-200 transition-colors"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Back to registration
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
