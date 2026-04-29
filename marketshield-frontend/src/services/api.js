import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,   // intel pipeline can take ~15s
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

// ── Legacy endpoints (kept for existing pages) ────────────────────────────
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

// ── Brand Intelligence endpoints (Person 1 / 2) ───────────────────────────

/** Full pipeline: scrape + LLM enrichment. Returns all 10 outputs. */
export const getFullIntel = (company_name, category = '') =>
  api.post('/company/full_intel', { company_name, category });

/** Alias used by spec / legacy code. */
export const getCompanyIntelligence = async (companyName, category = '') => {
  try {
    const response = await getFullIntel(companyName, category);
    return { success: true, data: response.data };
  } catch (error) {
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Failed to fetch intelligence',
    };
  }
};

/** Raw scrape only (no LLM). */
export const analyzeCompany = (company_name, category = '') =>
  api.post('/company/analyze', { company_name, category });

// ── Tracking endpoints (Person 1) ─────────────────────────────────────────

/** Generate a tracked redirect link. */
export const createTrackedLink = (target_url) =>
  api.post('/tracking/link', { target_url });

/** Query logged open/click events. */
export const getTrackingEvents = (company = '', recipient = '') =>
  api.get('/tracking/events', { params: { company, recipient } });

/** Get the pixel URL for a recipient (constructed client-side). */
export const pixelUrl = (eventId, recipient, company) =>
  `${API_BASE}/tracking/pixel/${eventId}?recipient=${encodeURIComponent(recipient)}&company=${encodeURIComponent(company)}`;
