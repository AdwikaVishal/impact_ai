/**
 * BrandActivity – sections #4 (news/brand activity) and #5 (events footprint).
 */
import { Newspaper, CalendarDays, ExternalLink, MapPin } from 'lucide-react';
import { motion } from 'framer-motion';
import SectionCard from './SectionCard';

function NewsItem({ item, index }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      className="flex items-start gap-3 py-3 border-b border-navy-700/30 last:border-0"
    >
      <div className="flex-shrink-0 w-16 text-center">
        <span className="text-xs text-navy-500 font-mono">{item.date?.slice(0, 10) || '—'}</span>
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-white leading-snug line-clamp-2">{item.title}</p>
        {item.source && (
          <span className="text-xs text-navy-500 mt-0.5 block">{item.source}</span>
        )}
      </div>
      {item.url && (
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-shrink-0 text-navy-600 hover:text-accent-400 transition-colors"
        >
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      )}
    </motion.div>
  );
}

function EventItem({ ev, index }) {
  const label = ev.snippet
    ? ev.snippet.slice(0, 100) + (ev.snippet.length > 100 ? '…' : '')
    : ev.source_url;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      className="flex items-start gap-3 py-2.5 border-b border-navy-700/30 last:border-0"
    >
      <div className="w-6 h-6 rounded-md bg-warning/10 border border-warning/20 flex items-center justify-center flex-shrink-0 mt-0.5">
        <MapPin className="w-3 h-3 text-warning" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-navy-300 leading-snug">{label}</p>
        {ev.platform && (
          <span className="text-xs text-warning/70 mt-0.5 block capitalize">{ev.platform}</span>
        )}
      </div>
      {ev.source_url && (
        <a
          href={ev.source_url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-shrink-0 text-navy-600 hover:text-accent-400 transition-colors"
        >
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      )}
    </motion.div>
  );
}

export default function BrandActivity({ data }) {
  const news   = (() => {
    const ba = data.brand_activity;
    // enricher returns brand_activity as {recent_items, ...}; raw pipeline returns array
    if (Array.isArray(ba)) return ba.slice(0, 12);
    if (ba?.recent_items) return ba.recent_items.slice(0, 12);
    return (data.brand_activity_summary || []).slice(0, 12);
  })();
  const events = (() => {
    const ef = data.events_footprint || data.event_footprint;
    if (ef?.events) return ef.events;
    return data.events || [];
  })();

  return (
    <div className="space-y-4">
      {/* #4 Brand Activity */}
      <SectionCard icon={Newspaper} title="Brand Activity" badge={`#4 · ${news.length} articles`}>
        {news.length === 0 ? (
          <p className="text-sm text-navy-500">No recent news found.</p>
        ) : (
          <div className="max-h-80 overflow-y-auto custom-scrollbar">
            {news.map((item, i) => <NewsItem key={i} item={item} index={i} />)}
          </div>
        )}
      </SectionCard>

      {/* #5 Events Footprint */}
      <SectionCard icon={CalendarDays} title="Events & Activations" badge={`#5 · ${events.length} found`}>
        {events.length === 0 ? (
          <p className="text-sm text-navy-500">No events found.</p>
        ) : (
          <div className="max-h-64 overflow-y-auto custom-scrollbar">
            {events.map((ev, i) => <EventItem key={i} ev={ev} index={i} />)}
          </div>
        )}
      </SectionCard>
    </div>
  );
}
