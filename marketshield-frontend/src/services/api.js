import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
});

// Interceptors for errors
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const analyzeHeadline = (headline) => 
  api.post('/analysis/', { headline });

export const getCompanyData = (symbol) => 
  api.get(`/market/${symbol}`);

export const searchCompanies = (query) => 
  api.get(`/market/search?q=${query}`);

export const getNews = (symbol) => 
  api.get(`/market/${symbol}/news`);

export const getPrediction = (symbol) => 
  api.get(`/market/${symbol}`);
