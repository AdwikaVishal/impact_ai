import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import NewsTicker from './components/NewsTicker';
import Dashboard from './pages/Dashboard';
import Analyzer from './pages/Analyzer';
import MarketOverview from './pages/MarketOverview';
import Watchlist from './pages/Watchlist';
import MarketIntelligence from './pages/MarketIntelligence';
import { Shield } from 'lucide-react';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-navy-950">
        {/* Fixed top bar */}
        <Navbar />
        <div className="pt-16">
          <NewsTicker />
        </div>

        {/* Page content */}
        <main className="pb-20">
          <Routes>
            <Route path="/"          element={<Dashboard />} />
            <Route path="/intel"     element={<MarketIntelligence />} />
            <Route path="/analyzer"  element={<Analyzer />} />
            <Route path="/market"    element={<MarketOverview />} />
            <Route path="/watchlist" element={<Watchlist />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="border-t border-white/5 bg-navy-950">
          <div className="max-w-[1400px] mx-auto px-6 sm:px-8 lg:px-16 py-8">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 bg-gradient-to-br from-accent-500 to-accent-cyan rounded-lg flex items-center justify-center">
                  <Shield className="w-4 h-4 text-white" />
                </div>
                <span className="text-sm font-semibold text-white">Impact AI</span>
              </div>
              <p className="text-xs text-navy-500">
                Brand Intelligence Engine · Powered by LLM + Web Scraping
              </p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
