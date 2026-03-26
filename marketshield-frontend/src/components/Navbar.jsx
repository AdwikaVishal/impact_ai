import { Shield, Zap, Activity, Home, Newspaper, Globe, Eye } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link, useLocation } from 'react-router-dom';

const Navbar = () => {
  const location = useLocation();
  
  const navLinks = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/analyzer', label: 'Analyzer', icon: Newspaper },
    { path: '/market', label: 'Markets', icon: Globe },
    { path: '/watchlist', label: 'Watchlist', icon: Eye },
  ];

  return (
    <motion.nav 
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="sticky top-0 z-50 backdrop-blur-xl bg-navy-900/80 border-b border-navy-700/50 shadow-lg"
    >
      <div className="max-w-[1400px] mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo Section */}
          <Link to="/" className="flex items-center space-x-4">
            <motion.div 
              whileHover={{ rotate: 360, scale: 1.1 }}
              transition={{ duration: 0.6 }}
              className="relative p-3 bg-gradient-to-br from-accent-500 via-accent-blue to-accent-cyan rounded-2xl shadow-glow-blue"
            >
              <Shield className="w-8 h-8 text-white" />
              <div className="absolute inset-0 bg-gradient-to-br from-accent-500 to-accent-cyan rounded-2xl blur-xl opacity-50 animate-pulse-slow"></div>
            </motion.div>
            <div>
              <h1 className="text-3xl font-bold gradient-text">
                MarketShield AI
              </h1>
              <p className="text-sm text-navy-500 font-medium">AI-Powered Financial Intelligence</p>
            </div>
          </Link>
          
          {/* Right Section - Navigation + Status */}
          <div className="flex items-center space-x-6">
            {/* Navigation Links */}
            <div className="hidden lg:flex items-center space-x-2">
              {navLinks.map((link) => {
                const Icon = link.icon;
                const isActive = location.pathname === link.path;
                
                return (
                  <Link
                    key={link.path}
                    to={link.path}
                    className="relative"
                  >
                    <motion.div
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className={`flex items-center space-x-2 px-4 py-2 rounded-xl transition-all ${
                        isActive 
                          ? 'bg-accent-500/20 text-accent-400 border border-accent-500/30' 
                          : 'text-navy-400 hover:text-white hover:bg-navy-800/50'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      <span className="text-sm font-medium">{link.label}</span>
                    </motion.div>
                    {isActive && (
                      <motion.div
                        layoutId="activeTab"
                        className="absolute bottom-0 left-0 right-0 h-0.5 bg-accent-400"
                        initial={false}
                        transition={{ type: "spring", stiffness: 500, damping: 30 }}
                      />
                    )}
                  </Link>
                );
              })}
            </div>

            {/* Divider */}
            <div className="hidden lg:block w-px h-8 bg-navy-700/50"></div>
            
            {/* Live Indicator */}
            <motion.div 
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-green-500/20 to-emerald-500/20 backdrop-blur-xl rounded-full border border-green-500/30"
            >
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-glow-cyan"></div>
              <Zap className="w-4 h-4 text-green-400" />
              <span className="text-xs font-semibold text-green-400">LIVE</span>
            </motion.div>
            
            {/* Stats */}
            <div className="hidden md:flex items-center space-x-2 px-4 py-2 bg-navy-800/50 rounded-lg border border-navy-700/50">
              <Activity className="w-4 h-4 text-accent-400" />
              <span className="text-xs text-navy-400">Real-time</span>
            </div>
          </div>
        </div>
      </div>
    </motion.nav>
  );
};

export default Navbar;

