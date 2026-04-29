/**
 * OutreachEditor – section #9: editable LinkedIn messages and email drafts.
 * Simulates sending and generates a tracking pixel URL.
 */
import { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Send, Linkedin, Mail, ChevronDown, CheckCircle2, Copy } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { pixelUrl } from '../../services/api';
import SectionCard from './SectionCard';

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    });
  };
  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1 text-xs text-navy-500 hover:text-accent-400 transition-colors"
    >
      {copied ? <CheckCircle2 className="w-3.5 h-3.5 text-success" /> : <Copy className="w-3.5 h-3.5" />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  );
}

function ContactCard({ contact, companyName }) {
  const [liMsg, setLiMsg]       = useState(contact.linkedin_message || '');
  const [subject, setSubject]   = useState(contact.email_subject || '');
  const [body, setBody]         = useState(contact.email_body || '');
  const [sent, setSent]         = useState(false);
  const [trackingId]            = useState(uuidv4());
  const [expanded, setExpanded] = useState(false);

  const email = contact.email && contact.email !== 'Not available'
    ? contact.email
    : contact.email_guesses?.[0] || '';

  const handleSimulateSend = () => {
    // Build the pixel URL that would be embedded in the real email
    const pixel = pixelUrl(trackingId, email, companyName);
    console.info('[OutreachEditor] Simulated send – pixel URL:', pixel);
    setSent(true);
    // Optionally: fetch the pixel to log an "open" event immediately for demo
    fetch(pixel).catch(() => {});
  };

  const hasContent = liMsg || subject || body;

  return (
    <div className="rounded-xl border border-navy-700/40 bg-navy-800/30 overflow-hidden">
      {/* Header */}
      <button
        onClick={() => setExpanded(v => !v)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-navy-800/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-accent-500/10 border border-accent-500/20 flex items-center justify-center text-sm font-bold text-accent-400">
            {(contact.name || '?')[0]?.toUpperCase()}
          </div>
          <div className="text-left">
            <p className="text-sm font-medium text-white">{contact.name || 'Unknown'}</p>
            <p className="text-xs text-navy-500">{contact.role || '—'}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {sent && <span className="text-xs text-success font-medium">Sent ✓</span>}
          {!hasContent && <span className="text-xs text-navy-600">No outreach generated</span>}
          <ChevronDown className={`w-4 h-4 text-navy-500 transition-transform ${expanded ? 'rotate-180' : ''}`} />
        </div>
      </button>

      {/* Expanded editor */}
      <AnimatePresence>
        {expanded && hasContent && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-4 border-t border-navy-700/30">

              {/* LinkedIn message */}
              {liMsg && (
                <div className="pt-4">
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="flex items-center gap-1.5 text-xs font-semibold text-navy-400">
                      <Linkedin className="w-3.5 h-3.5 text-[#0A66C2]" />
                      LinkedIn Message
                      <span className="text-navy-600">({liMsg.length}/300 chars)</span>
                    </label>
                    <CopyButton text={liMsg} />
                  </div>
                  <textarea
                    value={liMsg}
                    onChange={e => setLiMsg(e.target.value)}
                    maxLength={300}
                    rows={3}
                    className="w-full bg-navy-900/60 border border-navy-700/50 rounded-lg px-3 py-2 text-sm text-white placeholder-navy-600 focus:outline-none focus:border-accent-500/50 resize-none"
                  />
                </div>
              )}

              {/* Email */}
              {(subject || body) && (
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label className="flex items-center gap-1.5 text-xs font-semibold text-navy-400">
                      <Mail className="w-3.5 h-3.5 text-accent-400" />
                      Email Draft
                    </label>
                    <CopyButton text={`Subject: ${subject}\n\n${body}`} />
                  </div>
                  <input
                    value={subject}
                    onChange={e => setSubject(e.target.value)}
                    placeholder="Subject line"
                    className="w-full bg-navy-900/60 border border-navy-700/50 rounded-lg px-3 py-2 text-sm text-white placeholder-navy-600 focus:outline-none focus:border-accent-500/50 mb-2"
                  />
                  <textarea
                    value={body}
                    onChange={e => setBody(e.target.value)}
                    rows={6}
                    className="w-full bg-navy-900/60 border border-navy-700/50 rounded-lg px-3 py-2 text-sm text-white placeholder-navy-600 focus:outline-none focus:border-accent-500/50 resize-none"
                  />
                </div>
              )}

              {/* Send button */}
              <div className="flex items-center justify-between pt-1">
                {email && (
                  <span className="text-xs text-navy-500">
                    To: <span className="text-navy-400 font-mono">{email}</span>
                  </span>
                )}
                <button
                  onClick={handleSimulateSend}
                  disabled={sent}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-success/10 border border-success/20 text-success text-xs font-semibold hover:bg-success/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed ml-auto"
                >
                  <Send className="w-3.5 h-3.5" />
                  {sent ? 'Sent (simulated)' : 'Simulate Send'}
                </button>
              </div>

              {sent && (
                <p className="text-xs text-navy-500">
                  Tracking ID: <span className="font-mono text-navy-400">{trackingId}</span>
                  {' '}— check the Tracking tab to see open/click events.
                </p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function OutreachEditor({ data }) {
  const contacts    = data.decision_makers || data.contacts_raw || [];
  const companyName = data.company_name || '';
  const hasOutreach = contacts.some(c => c.linkedin_message || c.email_subject);

  return (
    <SectionCard icon={Send} title="Personalised Outreach" badge="#9">
      {!hasOutreach ? (
        <p className="text-sm text-navy-500">
          No outreach messages generated.
          {data._llm_backend === 'mock'
            ? ' Set OPENAI_API_KEY or start Ollama to enable LLM generation.'
            : ' Run /company/full_intel to generate messages.'}
        </p>
      ) : (
        <div className="space-y-2">
          <p className="text-xs text-navy-500 mb-3">
            Click a contact to expand and edit their LinkedIn message and email draft before sending.
          </p>
          {contacts.map((c, i) => (
            <ContactCard key={i} contact={c} companyName={companyName} />
          ))}
        </div>
      )}
    </SectionCard>
  );
}
