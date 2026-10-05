/**
 * ScoreCard — animated circular score display with gradient ring
 * and classification badge. Used in analysis results.
 */

import { useEffect, useState } from 'react';

const CLASSIFICATION_STYLES = {
  'Strong Match': 'score-strong',
  'Moderate Match': 'score-moderate',
  'Weak Match': 'score-weak',
  'Poor Match': 'score-poor',
};

const CLASSIFICATION_COLORS = {
  'Strong Match': '#10b981',
  'Moderate Match': '#f59e0b',
  'Weak Match': '#f97316',
  'Poor Match': '#ef4444',
};

export default function ScoreCard({ score = 0, classification = 'Unknown', size = 180 }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const radius = (size - 20) / 2;
  const circumference = 2 * Math.PI * radius;
  const center = size / 2;
  const strokeWidth = 10;

  useEffect(() => {
    // Animate the score from 0 to the target value
    const duration = 1500;
    const startTime = Date.now();
    const targetScore = Math.min(100, Math.max(0, score));

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setAnimatedScore(Math.round(targetScore * eased));

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [score]);

  const strokeDashoffset = circumference - (animatedScore / 100) * circumference;
  const color = CLASSIFICATION_COLORS[classification] || '#6366f1';

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          {/* Background circle */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="rgba(100, 116, 139, 0.15)"
            strokeWidth={strokeWidth}
          />
          {/* Score arc */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className="transition-all duration-100"
            style={{
              filter: `drop-shadow(0 0 8px ${color}50)`,
            }}
          />
          {/* Glow circle */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={2}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            opacity={0.3}
            style={{
              filter: `blur(4px)`,
            }}
          />
        </svg>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold font-display text-white">
            {animatedScore}
          </span>
          <span className="text-sm text-dark-400 font-medium">/ 100</span>
        </div>
      </div>

      {/* Classification badge */}
      <span className={CLASSIFICATION_STYLES[classification] || 'score-badge bg-dark-700 text-dark-300'}>
        {classification}
      </span>
    </div>
  );
}


/**
 * MiniScoreBar — horizontal score bar used in score breakdowns.
 */
export function MiniScoreBar({ label, score, weight, color = '#6366f1', maxScore = 100 }) {
  const [animatedWidth, setAnimatedWidth] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedWidth(score), 100);
    return () => clearTimeout(timer);
  }, [score]);

  const percentage = (animatedWidth / maxScore) * 100;

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <span className="text-dark-300 font-medium">{label}</span>
        <div className="flex items-center gap-2">
          <span className="text-dark-400 text-xs">({(weight * 100).toFixed(0)}%)</span>
          <span className="text-white font-semibold">{score.toFixed(1)}</span>
        </div>
      </div>
      <div className="h-2 bg-dark-700/50 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all duration-1000 ease-out"
          style={{
            width: `${percentage}%`,
            background: `linear-gradient(90deg, ${color}80, ${color})`,
            boxShadow: `0 0 12px ${color}40`,
          }}
        />
      </div>
    </div>
  );
}
