import { create } from 'zustand';
import { analyzeHeadline } from '../services/api';

export const useAnalysisStore = create((set, get) => ({
  // State
  analysis: null,
  marketData: null,
  isAnalyzing: false,
  selectedSymbol: 'NSE:NIFTY',
  error: null,
  
  // Actions
  setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),
  
  analyze: async (headline) => {
    set({ isAnalyzing: true, error: null });
    try {
      const { data } = await analyzeHeadline(headline);
      set({ 
        analysis: data,
        marketData: data.market_data,
        selectedSymbol: data.entities?.ticker || get().selectedSymbol,
        isAnalyzing: false
      });
    } catch (error) {
      console.error('Analysis failed:', error);
      set({ error: error.message, isAnalyzing: false });
    }
  },
  
  updateMarketData: (data) => set({ marketData: data }),
  
  clearAnalysis: () => set({ analysis: null, error: null }),
}));
