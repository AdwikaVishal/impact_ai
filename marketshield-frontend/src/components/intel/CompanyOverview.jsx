/**
 * CompanyOverview – sections #1 (overview) and #2 (market position).
 */
import { Building2, TrendingUp, Globe, Users, DollarSign, Calendar } from 'lucide-react';
import SectionCard from './SectionCard';

function MetaPill({ icon: Icon, label, value }) {
  if (!value) return null;
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-navy-800/60 border border-navy-700/40 text-xs">
      <Icon className="w-3.5 h-3.5 text-accent-400 flex-shrink-0" />
      <span className="text-navy-400">{label}:</span>
      <span className="text-white font-medium">{value}</span>
    </div>
  );
}

export default function CompanyOverview({ data }) {
  const scale = data.overview?.scale_indicators || {};
  const website = data.website;

  return (
    <div className="space-y-4">
      {/* #1 Company Overview */}
      <SectionCard icon={Building2} title="Company Overview" badge="#1">
        <p className="text-sm text-navy-300 leading-relaxed whitespace-pre-wrap">
          {data.company_overview || data.overview?.about_text?.slice(0, 400) || 'No overview available.'}
        </p>

        {/* Meta pills */}
        <div className="flex flex-wrap gap-2 mt-4">
          {website && (
            <a
              href={website}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-navy-800/60 border border-navy-700/40 text-xs text-accent-400 hover:text-accent-300 transition-colors"
            >
              <Globe className="w-3.5 h-3.5" />
              {data.domain || website}
            </a>
          )}
          <MetaPill icon={DollarSign} label="Revenue"   value={scale.revenue}   />
          <MetaPill icon={Users}       label="Employees" value={scale.employees} />
          <MetaPill icon={Calendar}    label="Founded"   value={scale.founded}   />
        </div>
      </SectionCard>

      {/* #2 Market Position */}
      <SectionCard icon={TrendingUp} title="Market Position" badge="#2">
        <p className="text-sm text-navy-300 leading-relaxed">
          {data.market_position || 'No market position analysis available.'}
        </p>
      </SectionCard>
    </div>
  );
}
