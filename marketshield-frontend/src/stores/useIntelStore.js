import { create } from 'zustand';

const useIntelStore = create((set) => ({
  // State
  loading:     false,
  error:       null,
  data:        null,
  companyName: '',
  category:    '',

  // Actions
  setLoading:     (loading)              => set({ loading }),
  setError:       (error)                => set({ error }),
  setData:        (data)                 => set({ data }),
  setCompanyInfo: (companyName, category) => set({ companyName, category }),
  reset:          ()                     => set({ loading: false, error: null, data: null }),
}));

export default useIntelStore;
