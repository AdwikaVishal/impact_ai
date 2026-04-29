/**
 * ScoreRing – animated circular progress showing the opportunity score (0-100).
 */
import { motion } from 'framer-motion';

const SIZE = 120;
const STROKE = 10;
const R = (SIZE - STROKE) / 2;
const CIRC = 2 * Math.PI * R;

function scoreColor(score) {
  if (score >= 70) return '#10b981'; // success green
  if (score >= 40) return '#f59e0b'; // warning amber
  return '#ef4444';                  // danger red
}

function scoreLabel(score) {
  if (score >= 70) return 'High';
  if (score >= 40) return 'Medium';
  return 'Low';
}

export default function ScoreRing({ score = 0, breakdown = {} }) {
  const color = scoreColor(score);
  const offset = CIRC - (score / 100) * CIRC;

  return (
    <div className="flex flex-col items-center gap-3">
      <svg width={SIZE} height={SIZE} className="-rotate-90">
        {/* Track */}
        <circle
          cx={SIZE / 2} cy={SIZE / 2} r={R}
          fill="none" stroke="#1e293b" strokeWidth={STROKE}
        />
        {/* Progress */}
        <motion.circle
          cx={SIZE / 2} cy={SIZE / 2} r={R}
          fill="none"
          stroke={color}
          strokeWidth={STROKE}
          strokeLinecap="round"
          strokeDasharray={CIRC}
          initial={{ strokeDashoffset: CIRC }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: 'easeOut' }}
        />
      </svg>
      {/* Label overlay */}
      <div className="flex flex-col items-center -mt-[88px] mb-[68px] pointer-events-none">
        <span className="text-2xl font-bold text-white">{score}</span>
        <span className="text-xs font-semibold" style={{ color }}>{scoreLabel(score)}</span>
      </div>

      {/* Breakdown pills */}
      {Object.keys(breakdown).length > 0 && (
        <div className="grid grid-cols-2 gap-1.5 w-full max-w-xs text-xs">
          {Object.entries(breakdown).map(([key, val]) => (
            <div key={key} className="flex justify-between px-2 py-1 rounded-lg bg-navy-800/60 border border-navy-700/40">
              <span className="text-navy-400 capitalize">{key.replace(/_/g, ' ')}</span>
              <span className={val < 0 ? 'text-danger' : 'text-accent-400'} style={{ fontVariantNumeric: 'tabular-nums' }}>
                {val > 0 ? `+${val}` : val}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
