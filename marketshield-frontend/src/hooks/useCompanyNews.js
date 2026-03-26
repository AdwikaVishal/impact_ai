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
        const response = await axios.get(`${API_BASE}/market/${symbol}/news`);
        
        if (response.data.success) {
          setNews(response.data.data);
        } else {
          setNews([]);
        }
      } catch (err) {
        console.error('Error fetching news:', err);
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
