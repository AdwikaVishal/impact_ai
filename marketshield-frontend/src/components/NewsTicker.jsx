import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const NewsTicker = () => {
  const [newsItems, setNewsItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  // Popular symbols to fetch news from
  const symbols = ['NASDAQ:AAPL', 'NASDAQ:TSLA', 'NASDAQ:MSFT', 'NASDAQ:GOOGL', 'NSE:RELIANCE', 'NSE:TCS'];

  useEffect(() => {
    const fetchAllNews = async () => {
      try {
        const allNews = [];
        
        // Fetch news from multiple companies
        for (const symbol of symbols) {
          try {
            const response = await axios.get(`${API_BASE}/market/${symbol}/news`);
            if (response.data.success && response.data.data.length > 0) {
              // Take first 2 news items from each company
              const companyNews = response.data.data.slice(0, 2).map(item => ({
                company: symbol.split(':')[1],
                text: item.title,
                sentiment: getSentiment(item.title),
                link: item.link
              }));
              allNews.push(...companyNews);
            }
          } catch (err) {
            console.error(`Error fetching news for ${symbol}:`, err);
          }
        }
        
        if (allNews.length > 0) {
          setNewsItems(allNews);
        }
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching news:', error);
        setIsLoading(false);
      }
    };

    fetchAllNews();
    
    // Refresh news every 5 minutes
    const interval = setInterval(fetchAllNews, 300000);
    return () => clearInterval(interval);
  }, []);

  const getSentiment = (title) => {
    const positive = ['surge', 'gain', 'high', 'rally', 'growth', 'profit', 'up', 'rise', 'boost', 'record', 'strong'];
    const negative = ['fall', 'drop', 'loss', 'down', 'decline', 'concern', 'risk', 'crash', 'weak', 'lawsuit'];
    
    const lowerTitle = title.toLowerCase();
    if (positive.some(word => lowerTitle.includes(word))) return 'positive';
    if (negative.some(word => lowerTitle.includes(word))) return 'negative';
    return 'neutral';
  };

  if (isLoading || newsItems.length === 0) {
    return (
      <div className="bg-navy-900/60 backdrop-blur-xl border-b border-navy-700/30 overflow-hidden">
        <div className="relative h-10 flex items-center justify-center">
          <span className="text-sm text-navy-400">Loading latest market news...</span>
        </div>
      </div>
    );
  }

  // Duplicate items for seamless loop
  const duplicatedNews = [...newsItems, ...newsItems, ...newsItems];

  return (
    <div className="bg-navy-900/60 backdrop-blur-xl border-b border-navy-700/30 overflow-hidden">
      <div className="relative h-10 flex items-center">
        {/* Gradient overlays for fade effect */}
        <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-navy-900/60 to-transparent z-10"></div>
        <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-navy-900/60 to-transparent z-10"></div>
        
        {/* Scrolling news - SLOWER SPEED */}
        <motion.div
          className="flex items-center space-x-12 whitespace-nowrap"
          animate={{
            x: ['0%', '-33.33%'],
          }}
          transition={{
            x: {
              repeat: Infinity,
              repeatType: "loop",
              duration: 120, // Increased from 60 to 120 seconds (2x slower)
              ease: "linear",
            },
          }}
        >
          {duplicatedNews.map((item, idx) => (
            <a
              key={idx}
              href={item.link}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-3 hover:opacity-80 transition-opacity"
            >
              <span className="text-xs font-mono font-bold text-accent-400 bg-accent-500/10 px-2 py-1 rounded">
                {item.company}
              </span>
              <span className="text-sm text-navy-300">{item.text}</span>
              {item.sentiment === 'positive' ? (
                <TrendingUp className="w-4 h-4 text-success" />
              ) : item.sentiment === 'negative' ? (
                <TrendingDown className="w-4 h-4 text-danger" />
              ) : (
                <div className="w-4 h-4" />
              )}
              <span className="text-navy-600">•</span>
            </a>
          ))}
        </motion.div>
      </div>
    </div>
  );
};

export default NewsTicker;
