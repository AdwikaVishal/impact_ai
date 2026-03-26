import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const useCompanySearch = (query) => {
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!query || query.length < 1) {
      setResults([]);
      return;
    }

    const searchCompanies = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await axios.get(`${API_BASE}/market/search`, {
          params: { q: query }
        });
        
        if (response.data.success) {
          setResults(response.data.data);
        } else {
          setResults([]);
        }
      } catch (err) {
        console.error('Error searching companies:', err);
        setError(err.message);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    };

    // Debounce search
    const timeoutId = setTimeout(searchCompanies, 300);
    return () => clearTimeout(timeoutId);
  }, [query]);

  return { results, isLoading, error };
};
