import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import NewsTicker from './components/NewsTicker';
import Dashboard from './pages/Dashboard';
import Analyzer from './pages/Analyzer';
import MarketOverview from './pages/MarketOverview';
import Watchlist from './pages/Watchlist';
import { Shield } from 'lucide-react';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-b from-navy-950 via-navy-900 to-black">
        <Navbar />
        <NewsTicker />
        
        {/* MAIN CONTENT */}
        <main className="pt-24 pb-20">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyzer" element={<Analyzer />} />
            <Route path="/market" element={<MarketOverview />} />
            <Route path="/watchlist" element={<Watchlist />} />
          </Routes>
        </main>

        {/* FOOTER - MINIMAL & CLEAN */}
        <footer className="border-t border-navy-700/30 bg-navy-950/80 backdrop-blur-xl">
          <div className="max-w-[1400px] mx-auto px-8 lg:px-16 py-12">
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex items-center space-x-3">
                <Shield className="w-6 h-6 text-accent-400" />
                <span className="text-lg font-bold text-white">MarketShield AI</span>
              </div>
              <p className="text-navy-500 text-sm">
                © 2024 MarketShield AI. Powered by 11 ML Models + Real-time Data
              </p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
