/**
 * CompetitorMapping – section #3: competitor strengths and gaps.
 */
import { Swords, CheckCircle2, XCircle, ExternalLink } from 'lucide-react';
import { motion } from 'framer-motion';
import SectionCard from './SectionCard';

function CompetitorRow({ comp, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.06 }}
      className="p-4 rounded-xl bg-navy-800/50 border border-navy-700/40 hover:border-accent-500/30 transition-colors"
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-accent-500/10 border border-accent-500/20 flex items-center justify-center text-xs font-bold text-accent-400">
            {(comp.name || '?')[0].toUpperCase()}
          </div>
          <span className="text-sm font-semibold text-white">{comp.name}</span>
        </div>
        {comp.website && (
          <a
            href={comp.website}
            target="_blank"
            rel="noopener noreferrer"
            className="text-navy-500 hover:text-accent-400 transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        )}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
        {comp.strength && (
          <div className="flex items-start gap-2 p-2 rounded-lg bg-success/5 border border-success/15">
            <CheckCircle2 className="w-3.5 h-3.5 text-success mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-success/70 font-medium mb-0.5">Strength</p>
              <p className="text-navy-300">{comp.strength}</p>
            </div>
          </div>
        )}
        {comp.gap && (
          <div className="flex items-start gap-2 p-2 rounded-lg bg-danger/5 border border-danger/15">
            <XCircle className="w-3.5 h-3.5 text-danger mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-danger/70 font-medium mb-0.5">Gap</p>
              <p className="text-navy-300">{comp.gap}</p>
            </div>
          </div>
        )}
      </div>

      {/* Recent activity */}
      {comp.recent_activity?.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {comp.recent_activity.slice(0, 2).map((a, i) => (
            <span key={i} className="text-xs px-2 py-0.5 rounded-full bg-navy-700/60 text-navy-400 truncate max-w-[200px]">
              {a}
            </span>
          ))}
        </div>
      )}
    </motion.div>
  );
}

export default function CompetitorMapping({ data }) {
  // Merge LLM analysis with raw competitor list
  const mapping = data.competitor_mapping || [];
  const raw = data.competitors || [];

  // Build a merged list: prefer LLM analysis, fall back to raw
  const merged = mapping.length > 0
    ? mapping.map(m => {
        const rawMatch = raw.find(r => r.name?.toLowerCase() === m.name?.toLowerCase());
        return { ...rawMatch, ...m };
      })
    : raw.map(r => ({ ...r, strength: null, gap: null }));

  return (
    <SectionCard icon={Swords} title="Competitor Mapping" badge={`#3 · ${merged.length} found`}>
      {merged.length === 0 ? (
        <p className="text-sm text-navy-500">No competitor data available.</p>
      ) : (
        <div className="space-y-3">
          {merged.map((comp, i) => (
            <CompetitorRow key={i} comp={comp} index={i} />
          ))}
        </div>
      )}
    </SectionCard>
  );
}
