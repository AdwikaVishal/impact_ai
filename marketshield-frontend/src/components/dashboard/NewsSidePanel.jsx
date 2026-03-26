import { motion } from 'framer-motion';
import { Newspaper, Clock, ExternalLink, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { useCompanyNews } from '../../hooks/useCompanyNews';

const getSentiment = (title) => {
  const t = title.toLowerCase();
  if (['surge','gain','high','rally','growth','profit','rise','boost','record'].some(w => t.includes(w))) return 'positive';
  if (['fall','drop','loss','down','decline','crash','risk','lawsuit','weak'].some(w => t.includes(w))) return 'negative';
  return 'neutral';
};

const timeAgo = (iso) => {
  const diff = Date.now() - new Date(iso);
  const m = Math.floor(diff / 60000);
  const h = Math.floor(diff / 3600000);
  const d = Math.floor(diff / 86400000);
  if (m < 60) return `${m}m ago`;
  if (h < 24) return `${h}h ago`;
  return `${d}d ago`;
};

const SentimentIcon = ({ s }) => {
  if (s === 'positive') return <TrendingUp className="w-3.5 h-3.5 text-success" />;
  if (s === 'negative') return <TrendingDown className="w-3.5 h-3.5 text-danger" />;
  return <Minus className="w-3.5 h-3.5 text-navy-500" />;
};

const sentimentStyle = {
  positive: 'bg-success/10 text-success border-success/20',
  negative: 'bg-danger/10 text-danger border-danger/20',
  neutral:  'bg-navy-700/40 text-navy-400 border-navy-700/40',
};

export default function NewsSidePanel({ selectedSymbol }) {
  const { news, isLoading } = useCompanyNews(selectedSymbol);
  const ticker = selectedSymbol?.split(':')[1] || selectedSymbol;

  if (isLoading) {
    return (
      <div className="bg-navy-900/50 border border-white/5 rounded-2xl p-5">
        <div className="flex items-center gap-3 mb-5">
          <div className="skeleton h-5 w-32 rounded" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="skeleton h-28 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-navy-900/50 border border-white/5 rounded-2xl overflow-hidden shadow-card"
    >
      {/* HEADER */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-white/5">
        <div className="flex items-center gap-2.5">
          <Newspaper className="w-4 h-4 text-accent-400" />
          <span className="text-sm font-semibold text-white">Latest News</span>
          <span className="text-xs font-mono text-navy-500 bg-navy-800/60 px-2 py-0.5 rounded-md">{ticker}</span>
        </div>
        <span className="text-xs text-navy-500">{news.length} articles</span>
      </div>

      {/* GRID */}
      <div className="p-5">
        {news.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {news.map((item, i) => {
              const s = getSentiment(item.title);
              return (
                <motion.a
                  key={i}
                  href={item.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.03 }}
                  whileHover={{ y: -2 }}
                  className="group flex flex-col gap-2.5 p-4 bg-navy-800/40 hover:bg-navy-800/70
                             border border-white/5 hover:border-accent-500/25 rounded-xl transition-all duration-200"
                >
                  {/* Top row */}
                  <div className="flex items-center justify-between">
                    <span className={`tag border ${sentimentStyle[s]}`}>
                      <span className="flex items-center gap-1">
                        <SentimentIcon s={s} />
                        {s.charAt(0).toUpperCase() + s.slice(1)}
                      </span>
                    </span>
                    <div className="flex items-center gap-1 text-xs text-navy-500">
                      <Clock className="w-3 h-3" />
                      {timeAgo(item.publishedAt)}
                    </div>
                  </div>

                  {/* Title */}
                  <p className="text-sm font-medium text-white leading-snug line-clamp-3
                                group-hover:text-accent-300 transition-colors flex-1">
                    {item.title}
                  </p>

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-1 border-t border-white/5">
                    <span className="text-xs text-navy-500 truncate max-w-[80%]">{item.publisher}</span>
                    <ExternalLink className="w-3.5 h-3.5 text-navy-600 group-hover:text-accent-400 transition-colors flex-shrink-0" />
                  </div>
                </motion.a>
              );
            })}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-navy-500">
            <Newspaper className="w-10 h-10 mb-3 opacity-30" />
            <p className="text-sm">No news available for {ticker}</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}
