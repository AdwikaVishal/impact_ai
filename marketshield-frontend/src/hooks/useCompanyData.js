import { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const useCompanyData = (symbol) => {
  const [companyData, setCompanyData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!symbol) return;

    const fetchCompanyData = async () => {
      setIsLoading(true);
      setError(null);

      try {
        // Fetch from our backend API (which proxies to yfinance)
        const response = await axios.get(`${API_BASE}/market/${symbol}`);
        
        if (response.data.success) {
          setCompanyData(response.data.data);
        } else {
          throw new Error('Failed to fetch data');
        }
      } catch (err) {
        console.error('Error fetching company data:', err);
        // Fallback to static data
        setCompanyData(getStaticCompanyData(symbol));
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCompanyData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchCompanyData, 30000);
    return () => clearInterval(interval);
  }, [symbol]);

  return { companyData, isLoading, error };
};

// Fallback static data
const getStaticCompanyData = (symbol) => {
  const companies = {
    'NSE:NIFTY': { 
      name: 'NIFTY 50', 
      ticker: 'NIFTY', 
      exchange: 'NSE', 
      price: 24150.75, 
      previousClose: 23650.50,
      change: 500.25,
      changePercent: 2.14, 
      volume: 2400000,
      marketCap: 0,
      currency: 'INR' 
    },
    'BSE:SENSEX': { 
      name: 'SENSEX', 
      ticker: 'SENSEX', 
      exchange: 'BSE', 
      price: 79486.32, 
      previousClose: 78000.00,
      change: 1486.32,
      changePercent: 1.89, 
      volume: 1800000,
      marketCap: 0,
      currency: 'INR' 
    },
    'NSE:RELIANCE': { 
      name: 'Reliance Industries', 
      ticker: 'RELIANCE', 
      exchange: 'NSE', 
      price: 2845.60, 
      previousClose: 2810.50,
      change: 35.10,
      changePercent: 1.23, 
      volume: 5600000,
      marketCap: 19200000000000,
      currency: 'INR' 
    },
    'NSE:TCS': { 
      name: 'Tata Consultancy Services', 
      ticker: 'TCS', 
      exchange: 'NSE', 
      price: 3892.45, 
      previousClose: 3859.00,
      change: 33.45,
      changePercent: 0.87, 
      volume: 1200000,
      marketCap: 14200000000000,
      currency: 'INR' 
    },
    'NSE:HDFCBANK': { 
      name: 'HDFC Bank', 
      ticker: 'HDFCBANK', 
      exchange: 'NSE', 
      price: 1654.30, 
      previousClose: 1661.80,
      change: -7.50,
      changePercent: -0.45, 
      volume: 8900000,
      marketCap: 12500000000000,
      currency: 'INR' 
    },
    'NSE:INFY': { 
      name: 'Infosys', 
      ticker: 'INFY', 
      exchange: 'NSE', 
      price: 1523.75, 
      previousClose: 1500.00,
      change: 23.75,
      changePercent: 1.56, 
      volume: 4500000,
      marketCap: 6300000000000,
      currency: 'INR' 
    },
    'NASDAQ:TSLA': { 
      name: 'Tesla Inc.', 
      ticker: 'TSLA', 
      exchange: 'NASDAQ', 
      price: 241.18, 
      previousClose: 246.50,
      change: -5.32,
      changePercent: -2.14, 
      volume: 85600000,
      marketCap: 765000000000,
      currency: 'USD' 
    },
    'NASDAQ:AAPL': { 
      name: 'Apple Inc.', 
      ticker: 'AAPL', 
      exchange: 'NASDAQ', 
      price: 178.32, 
      previousClose: 175.75,
      change: 2.57,
      changePercent: 1.45, 
      volume: 52300000,
      marketCap: 2800000000000,
      currency: 'USD' 
    },
    'NASDAQ:MSFT': { 
      name: 'Microsoft Corporation', 
      ticker: 'MSFT', 
      exchange: 'NASDAQ', 
      price: 412.56, 
      previousClose: 408.56,
      change: 4.00,
      changePercent: 0.98, 
      volume: 23400000,
      marketCap: 3100000000000,
      currency: 'USD' 
    },
    'NASDAQ:NVDA': { 
      name: 'NVIDIA Corporation', 
      ticker: 'NVDA', 
      exchange: 'NASDAQ', 
      price: 875.28, 
      previousClose: 848.00,
      change: 27.28,
      changePercent: 3.21, 
      volume: 45600000,
      marketCap: 2200000000000,
      currency: 'USD' 
    },
  };

  return companies[symbol] || companies['NSE:NIFTY'];
};
