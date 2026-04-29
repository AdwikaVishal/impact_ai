/**
 * TrackingDashboard – section #10: email open/click event log.
 */
import { useEffect, useState, useCallback } from 'react';
import { Activity, RefreshCw, Mail, MousePointer, Clock } from 'lucide-react';
import { motion } from 'framer-motion';
import { getTrackingEvents } from '../../services/api';
import SectionCard from './SectionCard';

const EVENT_ICONS = {
  open:  { icon: Mail,         color: 'text-success',  bg: 'bg-success/10',  border: 'border-success/20'  },
  click: { icon: MousePointer, color: 'text-accent-400', bg: 'bg-accent-500/10', border: 'border-accent-500/20' },
};

function EventRow({ ev, index }) {
  const cfg = EVENT_ICONS[ev.event_type] || EVENT_ICONS.open;
  const Icon = cfg.icon;

  return (
    <motion.tr
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
      className="border-b border-navy-700/20 hover:bg-navy-800/20 transition-colors"
    >
      <td className="py-2.5 px-3">
        <div className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium ${cfg.bg} ${cfg.border} border ${cfg.color}`}>
          <Icon className="w-3 h-3" />
          {ev.event_type}
        </div>
      </td>
      <td className="py-2.5 px-3 text-xs text-navy-300 font-mono truncate max-w-[160px]">
        {ev.recipient || '—'}
      </td>
      <td className="py-2.5 px-3 text-xs text-navy-400">
        {ev.company || '—'}
      </td>
      <td className="py-2.5 px-3">
        <div className="flex items-center gap-1 text-xs text-navy-500">
          <Clock className="w-3 h-3" />
          {ev.timestamp ? new Date(ev.timestamp).toLocaleString() : '—'}
        </div>
      </td>
    </motion.tr>
  );
}

export default function TrackingDashboard({ companyFilter = '' }) {
  const [events,   setEvents]   = useState([]);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState('');
  const [lastFetch, setLastFetch] = useState(null);

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await getTrackingEvents(companyFilter);
      setEvents(res.data || []);
      setLastFetch(new Date());
    } catch (err) {
      setError('Could not load tracking events. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, [companyFilter]);

  useEffect(() => {
    fetchEvents();
    // Auto-refresh every 10 seconds
    const interval = setInterval(fetchEvents, 10000);
    return () => clearInterval(interval);
  }, [fetchEvents]);

  const opens  = events.filter(e => e.event_type === 'open').length;
  const clicks = events.filter(e => e.event_type === 'click').length;

  return (
    <SectionCard icon={Activity} title="Email Tracking & Engagement" badge="#10">
      {/* Stats strip */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        {[
          { label: 'Total Events', value: events.length, color: 'text-white' },
          { label: 'Opens',        value: opens,         color: 'text-success' },
          { label: 'Clicks',       value: clicks,        color: 'text-accent-400' },
        ].map(({ label, value, color }) => (
          <div key={label} className="p-3 rounded-xl bg-navy-800/50 border border-navy-700/40 text-center">
            <p className={`text-xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-navy-500 mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* Refresh row */}
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs text-navy-600">
          {lastFetch ? `Last updated ${lastFetch.toLocaleTimeString()}` : 'Loading…'}
        </p>
        <button
          onClick={fetchEvents}
          disabled={loading}
          className="flex items-center gap-1.5 text-xs text-navy-400 hover:text-accent-400 transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {error && (
        <p className="text-xs text-danger mb-3">{error}</p>
      )}

      {events.length === 0 && !loading ? (
        <div className="text-center py-8">
          <Activity className="w-8 h-8 text-navy-700 mx-auto mb-2" />
          <p className="text-sm text-navy-500">No tracking events yet.</p>
          <p className="text-xs text-navy-600 mt-1">
            Use "Simulate Send" in the Outreach tab to generate events.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto max-h-72 overflow-y-auto custom-scrollbar">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-navy-900/90 backdrop-blur-sm">
              <tr className="border-b border-navy-700/50">
                <th className="text-left py-2 px-3 text-xs font-semibold text-navy-500 uppercase tracking-wider">Event</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-navy-500 uppercase tracking-wider">Recipient</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-navy-500 uppercase tracking-wider">Company</th>
                <th className="text-left py-2 px-3 text-xs font-semibold text-navy-500 uppercase tracking-wider">Time</th>
              </tr>
            </thead>
            <tbody>
              {events.map((ev, i) => <EventRow key={ev.id || i} ev={ev} index={i} />)}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-xs text-navy-600 mt-3">
        Tracking pixels and unique redirect links are generated per email.
        Opens and clicks are logged to the backend SQLite database.
      </p>
    </SectionCard>
  );
}
