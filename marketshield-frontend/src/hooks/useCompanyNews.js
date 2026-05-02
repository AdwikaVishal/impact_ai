import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const useCompanyNews = (symbol) => {
  const [news, setNews] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!symbol) return;

    const fetchNews = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // GNews.io API is fast - 3 second timeout
        const response = await axios.get(`${API_BASE}/market/${symbol}/news`, {
          timeout: 3000
        });
        
        if (response.data.success) {
          setNews(response.data.data);
        } else {
          setNews([]);
        }
      } catch (err) {
        if (err.code === 'ECONNABORTED') {
          console.warn('News request timed out for', symbol);
        } else {
          console.error('Error fetching news:', err);
        }
        setError(err.message);
        setNews([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNews();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchNews, 300000);
    return () => clearInterval(interval);
  }, [symbol]);

  return { news, isLoading, error };
};
