/**
 * ResultsView – tabbed container for all 10 output sections.
 */
import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Building2, TrendingUp, Swords, Newspaper,
  AlertTriangle, Users, Send, Activity,
} from 'lucide-react';

import CompanyOverview    from './CompanyOverview';
import CompetitorMapping  from './CompetitorMapping';
import BrandActivity      from './BrandActivity';
import StrategicWatchouts from './StrategicWatchouts';
import DecisionMakers     from './DecisionMakers';
import OutreachEditor     from './OutreachEditor';
import TrackingDashboard  from './TrackingDashboard';

const TABS = [
  { id: 'overview',     label: 'Overview',     icon: Building2,    sections: '1–2' },
  { id: 'competitors',  label: 'Competitors',  icon: Swords,       sections: '3'   },
  { id: 'activity',     label: 'Activity',     icon: Newspaper,    sections: '4–5' },
  { id: 'watchouts',    label: 'Watchouts',    icon: AlertTriangle, sections: '6'  },
  { id: 'people',       label: 'People',       icon: Users,        sections: '7–8' },
  { id: 'outreach',     label: 'Outreach',     icon: Send,         sections: '9'   },
  { id: 'tracking',     label: 'Tracking',     icon: Activity,     sections: '10'  },
];

export default function ResultsView({ data }) {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="mt-6">
      {/* LLM backend badge */}
      {data._llm_backend && (
        <div className="flex items-center gap-2 mb-4">
          <span className="text-xs text-navy-500">LLM backend:</span>
          <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${
            data._llm_backend === 'openai'
              ? 'bg-success/10 border-success/20 text-success'
              : data._llm_backend === 'ollama'
              ? 'bg-warning/10 border-warning/20 text-warning'
              : 'bg-navy-800 border-navy-700 text-navy-400'
          }`}>
            {data._llm_backend}
          </span>
          {data.opportunity_score != null && (
            <>
              <span className="text-xs text-navy-500 ml-2">Opportunity score:</span>
              <span className="text-xs font-bold text-white">{data.opportunity_score}/100</span>
            </>
          )}
        </div>
      )}

      {/* Tab bar */}
      <div className="flex flex-wrap gap-1 mb-4 p-1 bg-navy-900/60 border border-navy-700/40 rounded-xl">
        {TABS.map(({ id, label, icon: Icon, sections }) => {
          const active = activeTab === id;
          return (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={`relative flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200 ${
                active
                  ? 'text-white'
                  : 'text-navy-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {active && (
                <motion.div
                  layoutId="tab-bg"
                  className="absolute inset-0 bg-accent-500/15 border border-accent-500/25 rounded-lg"
                  transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                />
              )}
              <Icon className="w-3.5 h-3.5 relative z-10" />
              <span className="relative z-10">{label}</span>
              <span className="relative z-10 text-navy-600 text-[10px]">#{sections}</span>
            </button>
          );
        })}
      </div>

      {/* Tab content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === 'overview'    && <CompanyOverview    data={data} />}
          {activeTab === 'competitors' && <CompetitorMapping  data={data} />}
          {activeTab === 'activity'    && <BrandActivity      data={data} />}
          {activeTab === 'watchouts'   && <StrategicWatchouts data={data} />}
          {activeTab === 'people'      && <DecisionMakers     data={data} />}
          {activeTab === 'outreach'    && <OutreachEditor      data={data} />}
          {activeTab === 'tracking'    && <TrackingDashboard  companyFilter={data.company_name} />}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
