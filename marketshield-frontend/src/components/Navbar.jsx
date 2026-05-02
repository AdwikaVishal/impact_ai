import { useState } from 'react';
import { Shield, Zap, Home, Newspaper, Globe, Eye, Building2, Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';

const navLinks = [
  { path: '/', label: 'Dashboard', icon: Home },
  { path: '/analyzer', label: 'Analyzer', icon: Newspaper },
  { path: '/comparison', label: 'Comparison', icon: Building2 },
  { path: '/market', label: 'Markets', icon: Globe },
  { path: '/watchlist', label: 'Watchlist', icon: Eye },
];

export default function Navbar() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <motion.nav
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="fixed top-0 left-0 right-0 z-50 backdrop-blur-2xl bg-navy-950/80 border-b border-white/5"
      >
        <div className="max-w-[1400px] mx-auto px-4 sm:px-8 lg:px-16 h-16 flex items-center justify-between">
          {/* LOGO */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative w-9 h-9 flex items-center justify-center bg-gradient-to-br from-accent-500 to-accent-cyan rounded-xl shadow-glow-blue group-hover:shadow-glow-cyan transition-all duration-300">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div className="hidden sm:block">
              <span className="text-base font-bold text-white tracking-tight">MarketShield</span>
              <span className="ml-1.5 text-xs font-semibold text-accent-400 bg-accent-500/10 px-1.5 py-0.5 rounded-md">AI</span>
            </div>
          </Link>

          {/* DESKTOP NAV */}
          <div className="hidden lg:flex items-center gap-1">
            {navLinks.map(({ path, label, icon: Icon }) => {
              const active = location.pathname === path;
              return (
                <Link key={path} to={path} className="relative px-4 py-2 rounded-xl group">
                  <div className={`flex items-center gap-2 text-sm font-medium transition-colors duration-200 ${
                    active ? 'text-white' : 'text-navy-400 group-hover:text-white'
                  }`}>
                    <Icon className="w-4 h-4" />
                    {label}
                  </div>
                  {active && (
                    <motion.div
                      layoutId="nav-pill"
                      className="absolute inset-0 bg-white/8 rounded-xl border border-white/10"
                      transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                    />
                  )}
                </Link>
              );
            })}
          </div>

          {/* RIGHT SIDE */}
          <div className="flex items-center gap-3">
            {/* Live badge */}
            <div className="flex items-center gap-2 px-3 py-1.5 bg-success/10 border border-success/20 rounded-full">
              <span className="w-1.5 h-1.5 rounded-full bg-success live-dot" />
              <Zap className="w-3 h-3 text-success" />
              <span className="text-xs font-semibold text-success hidden sm:block">LIVE</span>
            </div>

            {/* Mobile menu toggle */}
            <button
              onClick={() => setMobileOpen(v => !v)}
              className="lg:hidden p-2 rounded-xl bg-navy-800/60 border border-navy-700/50 text-navy-400 hover:text-white transition-colors"
              aria-label="Toggle menu"
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </motion.nav>

      {/* MOBILE MENU */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="fixed top-16 left-0 right-0 z-40 bg-navy-950/95 backdrop-blur-2xl border-b border-white/5 lg:hidden"
          >
            <div className="max-w-[1400px] mx-auto px-4 py-4 flex flex-col gap-1">
              {navLinks.map(({ path, label, icon: Icon }) => {
                const active = location.pathname === path;
                return (
                  <Link
                    key={path}
                    to={path}
                    onClick={() => setMobileOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                      active
                        ? 'bg-accent-500/15 text-white border border-accent-500/20'
                        : 'text-navy-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {label}
                  </Link>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
