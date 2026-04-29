/**
 * DecisionMakers – sections #7 (people table) and #8 (opportunity score).
 */
import { Users, ExternalLink, Mail, Linkedin, Target } from 'lucide-react';
import { motion } from 'framer-motion';
import SectionCard from './SectionCard';
import ScoreRing from './ScoreRing';

function ContactRow({ contact, index }) {
  const email = contact.email && contact.email !== 'Not available'
    ? contact.email
    : contact.email_guesses?.[0]
    || null;

  return (
    <motion.tr
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: index * 0.05 }}
      className="border-b border-navy-700/30 hover:bg-navy-800/30 transition-colors"
    >
      <td className="py-3 px-3">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-accent-500/10 border border-accent-500/20 flex items-center justify-center text-xs font-bold text-accent-400 flex-shrink-0">
            {(contact.name || '?')[0]?.toUpperCase()}
          </div>
          <span className="text-sm text-white font-medium">{contact.name || 'Unknown'}</span>
        </div>
      </td>
      <td className="py-3 px-3 text-xs text-navy-400">{contact.role || '—'}</td>
      <td className="py-3 px-3">
        {email ? (
          <div className="flex items-center gap-1.5">
            <Mail className="w-3 h-3 text-navy-500 flex-shrink-0" />
            <span className="text-xs text-navy-300 font-mono truncate max-w-[160px]">{email}</span>
            {contact.email_guesses?.length > 0 && (
              <span className="text-xs text-navy-600">(guessed)</span>
            )}
          </div>
        ) : (
          <span className="text-xs text-navy-600">Not found</span>
        )}
      </td>
      <td className="py-3 px-3">
        {contact.linkedin_url ? (
          <a
            href={contact.linkedin_url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-xs text-accent-400 hover:text-accent-300 transition-colors"
          >
            <Linkedin className="w-3.5 h-3.5" />
            Profile
            <ExternalLink className="w-2.5 h-2.5" />
          </a>
        ) : (
          <span className="text-xs text-navy-600">—</span>
        )}
      </td>
    </motion.tr>
  );
}

export default function DecisionMakers({ data }) {
  const contacts = data.decision_makers || data.contacts_raw || [];
  const score    = data.opportunity_score ?? null;
  const breakdown = data.score_breakdown || {};

  return (
    <div className="space-y-4">
      {/* #7 Decision Makers */}
      <SectionCard icon={Users} title="Decision Makers & Contacts" badge={`#7 · ${contacts.length} found`}>
        {contacts.length === 0 ? (
          <p className="text-sm text-navy-500">No decision-makers found.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-navy-700/50">
                  <th className="text-left py-2 px-3 text-xs font-semibold text-navy-500 uppercase tracking-wider">Name</th>
                  <th className="text-left py-2 px-3 text-xs font-semibold text-navy-500 uppercase tracking-wider">Role</th>
                  <th className="text-left py-2 px-3 text-xs font-semibold text-navy-500 uppercase tracking-wider">Email</th>
                  <th className="text-left py-2 px-3 text-xs font-semibold text-navy-500 uppercase tracking-wider">LinkedIn</th>
                </tr>
              </thead>
              <tbody>
                {contacts.map((c, i) => <ContactRow key={i} contact={c} index={i} />)}
              </tbody>
            </table>
          </div>
        )}
      </SectionCard>

      {/* #8 Opportunity Score */}
      {score !== null && (
        <SectionCard icon={Target} title="Opportunity Score" badge="#8">
          <div className="flex flex-col sm:flex-row items-center gap-6">
            <ScoreRing score={score} breakdown={breakdown} />
            <div className="flex-1 text-sm text-navy-400 leading-relaxed">
              <p className="text-white font-medium mb-1">What this means</p>
              <p>
                Score of <span className="text-white font-semibold">{score}/100</span> based on
                campaign activity in news, event footprint, competitor pressure, and contact data quality.
              </p>
              {score >= 70 && <p className="mt-2 text-success">Strong outreach opportunity — brand is actively spending on marketing.</p>}
              {score >= 40 && score < 70 && <p className="mt-2 text-warning">Moderate opportunity — some signals present, timing may vary.</p>}
              {score < 40 && <p className="mt-2 text-danger">Low opportunity — limited marketing activity detected.</p>}
            </div>
          </div>
        </SectionCard>
      )}
    </div>
  );
}
