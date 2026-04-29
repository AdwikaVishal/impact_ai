/**
 * SectionCard – consistent wrapper for each of the 10 output sections.
 */
import { motion } from 'framer-motion';

export default function SectionCard({ icon: Icon, title, badge, children, className = '' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className={`glass-card p-5 ${className}`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2.5">
          {Icon && (
            <div className="w-8 h-8 rounded-lg bg-accent-500/10 border border-accent-500/20 flex items-center justify-center flex-shrink-0">
              <Icon className="w-4 h-4 text-accent-400" />
            </div>
          )}
          <h3 className="text-sm font-semibold text-white">{title}</h3>
        </div>
        {badge != null && (
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-accent-500/10 text-accent-400 border border-accent-500/20">
            {badge}
          </span>
        )}
      </div>
      {children}
    </motion.div>
  );
}
