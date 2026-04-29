/**
 * StrategicWatchouts – section #6: 3 LLM-generated risk bullets.
 */
import { AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import SectionCard from './SectionCard';

const COLORS = [
  { bg: 'bg-danger/5',   border: 'border-danger/20',   text: 'text-danger',   dot: 'bg-danger'   },
  { bg: 'bg-warning/5',  border: 'border-warning/20',  text: 'text-warning',  dot: 'bg-warning'  },
  { bg: 'bg-info/5',     border: 'border-info/20',     text: 'text-info',     dot: 'bg-info'     },
];

export default function StrategicWatchouts({ data }) {
  const watchouts = data.strategic_watchouts || [];

  return (
    <SectionCard icon={AlertTriangle} title="Strategic Watchouts" badge="#6">
      {watchouts.length === 0 ? (
        <p className="text-sm text-navy-500">No watchouts generated.</p>
      ) : (
        <div className="space-y-3">
          {watchouts.map((w, i) => {
            const c = COLORS[i % COLORS.length];
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.1 }}
                className={`flex items-start gap-3 p-4 rounded-xl ${c.bg} border ${c.border}`}
              >
                <span className={`w-2 h-2 rounded-full ${c.dot} mt-1.5 flex-shrink-0`} />
                <p className="text-sm text-navy-200 leading-relaxed">{w}</p>
              </motion.div>
            );
          })}
        </div>
      )}
    </SectionCard>
  );
}
