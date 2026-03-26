import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Radio } from 'lucide-react';
import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
const SYMBOLS = ['NASDAQ:AAPL', 'NASDAQ:TSLA', 'NASDAQ:NVDA', 'NSE:RELIANCE', 'NSE:TCS'];

const getSentiment = (title) => {
  const t = title.toLowerCase();
  if (['surge','gain','high','rally','growth','profit','rise','boost','record','strong'].some(w => t.includes(w))) return 'positive';
  if (['fall','drop','loss','down','decline','crash','weak','lawsuit','risk'].some(w => t.includes(w))) return 'negative';
  return 'neutral';
};

export default function NewsTicker() {
  const [items, setItems] = useState([]);

  useEffect(() => {
    const fetch = async () => {
      const all = [];
      for (const sym of SYMBOLS) {
        try {
          const r = await axios.get(`${API_BASE}/market/${sym}/news`);
          if (r.data.success) {
            r.data.data.slice(0, 2).forEach(n => all.push({
              company: sym.split(':')[1] || sym,
              text: n.title,
              sentiment: getSentiment(n.title),
              link: n.link,
            }));
          }
        } catch {}
      }
      if (all.length) setItems(all);
    };
    fetch();
    const t = setInterval(fetch, 300000);
    return () => clearInterval(t);
  }, []);

  if (!items.length) return (
    <div className="h-9 bg-navy-950/90 border-b border-white/5 flex items-center justify-center">
      <span className="text-xs text-navy-500 animate-pulse">Loading market news…</span>
    </div>
  );

  const doubled = [...items, ...items, ...items];

  return (
    <div className="h-9 bg-navy-950/90 border-b border-white/5 overflow-hidden relative flex items-center">
      {/* Left fade */}
      <div className="absolute left-0 top-0 bottom-0 w-20 bg-gradient-to-r from-navy-950 to-transparent z-10 pointer-events-none" />
      {/* Right fade */}
      <div className="absolute right-0 top-0 bottom-0 w-20 bg-gradient-to-l from-navy-950 to-transparent z-10 pointer-events-none" />

      {/* LIVE label */}
      <div className="absolute left-3 z-20 flex items-center gap-1.5 bg-navy-950/90 pr-3">
        <Radio className="w-3 h-3 text-success" />
        <span className="text-xs font-bold text-success tracking-widest">LIVE</span>
        <div className="w-px h-4 bg-navy-700 ml-1" />
      </div>

      <motion.div
        className="flex items-center gap-10 pl-24 whitespace-nowrap"
        animate={{ x: ['0%', '-33.33%'] }}
        transition={{ x: { repeat: Infinity, repeatType: 'loop', duration: 90, ease: 'linear' } }}
      >
        {doubled.map((item, i) => (
          <a
            key={i}
            href={item.link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2.5 hover:opacity-80 transition-opacity"
          >
            <span className="text-xs font-bold font-mono text-accent-400">{item.company}</span>
            <span className="text-xs text-navy-300">{item.text}</span>
            {item.sentiment === 'positive'
              ? <TrendingUp className="w-3 h-3 text-success flex-shrink-0" />
              : item.sentiment === 'negative'
              ? <TrendingDown className="w-3 h-3 text-danger flex-shrink-0" />
              : <Minus className="w-3 h-3 text-navy-500 flex-shrink-0" />}
            <span className="text-navy-700">·</span>
          </a>
        ))}
      </motion.div>
    </div>
  );
}
