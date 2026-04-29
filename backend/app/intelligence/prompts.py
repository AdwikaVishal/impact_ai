"""
prompts.py – All LLM prompt templates for the intelligence layer.

Each template uses Python .format() placeholders.
Keep prompts focused and instruct the model to use ONLY provided data
to prevent hallucination.
"""

# ---------------------------------------------------------------------------
# Company overview
# ---------------------------------------------------------------------------

COMPANY_OVERVIEW_PROMPT = """\
You are a senior market research analyst. Using ONLY the "About" text below \
(do not add external knowledge), write a concise company overview of 2-3 sentences covering:
1. Business model (how they make money)
2. Scale (mention revenue/employees only if explicitly stated in the text)
3. Market positioning (premium / mass-market / innovator / challenger / etc.)

About text:
{about_text}

Return ONLY the overview as plain text. No bullet points, no headers, no extra commentary.
If the text is insufficient, respond with exactly: "Insufficient data to generate overview."
"""

# ---------------------------------------------------------------------------
# Market position
# ---------------------------------------------------------------------------

MARKET_POSITION_PROMPT = """\
You are a brand strategist. Based ONLY on the news headlines below about {company_name}, \
write 2-3 sentences describing:
1. Current brand perception (positive / negative / mixed)
2. Any recent shifts in strategy, reputation, or market focus visible in the headlines

News headlines (most recent first):
{news_list}

Return ONLY the market position analysis as plain text.
If there are no headlines, respond with exactly: "No recent news available to assess market position."
"""

# ---------------------------------------------------------------------------
# Competitor analysis
# ---------------------------------------------------------------------------

COMPETITOR_GAPS_PROMPT = """\
You are a competitive intelligence analyst. Using ONLY the competitor data below, \
analyse each competitor for {company_name} in the {category} space.

Competitors and their recent activity:
{competitors_list}

Return a JSON array (and nothing else) where each element has exactly these keys:
  "name"     – competitor name
  "strength" – one key competitive strength (based on their activity)
  "gap"      – one key weakness or gap visible from the data

Example format:
[
  {{"name": "Adidas", "strength": "strong soccer sponsorships", "gap": "limited direct-to-consumer presence"}},
  {{"name": "Puma", "strength": "celebrity collaborations", "gap": "smaller retail footprint"}}
]

If no competitor data is available, return an empty array: []
"""

# ---------------------------------------------------------------------------
# Strategic watchouts
# ---------------------------------------------------------------------------

STRATEGIC_WATCHOUTS_PROMPT = """\
You are a strategic advisor preparing a briefing for a marketing agency about to pitch {company_name}.
Using ONLY the data provided below, identify exactly 3 strategic watchouts \
(risks, tensions, or blind spots the agency should know before engaging).

Data:
- Recent news headlines: {news_summary}
- Key competitors: {competitor_summary}
- Known events / activations: {events_summary}

Return EXACTLY 3 bullet points, each starting with "- " and no more than 25 words each.
Base every point strictly on the provided data. Do not invent facts.
"""

# ---------------------------------------------------------------------------
# Opportunity angle (used internally to personalise outreach)
# ---------------------------------------------------------------------------

OPPORTUNITY_ANGLE_PROMPT = """\
In one sentence (max 20 words), describe the most compelling marketing opportunity \
for an agency approaching {company_name} based on this recent activity:
{activity_summary}

Return ONLY the one-sentence opportunity angle.
"""

# ---------------------------------------------------------------------------
# LinkedIn message
# ---------------------------------------------------------------------------

LINKEDIN_MESSAGE_PROMPT = """\
Write a short LinkedIn connection message (150-250 characters) to {decision_maker_name}, \
{role} at {company_name}.

Context – their recent brand activity:
{recent_activity_summary}

Opportunity angle:
{opportunity_angle}

Rules:
- Professional but warm tone
- Reference ONE specific recent activity from the context
- End with a soft call to action (e.g., "Would love to connect.")
- Return ONLY the message text, no subject line, no quotes
"""

# ---------------------------------------------------------------------------
# Email draft
# ---------------------------------------------------------------------------

EMAIL_DRAFT_PROMPT = """\
Write a professional outreach email to {decision_maker_name}, {role} at {company_name}.

Recent brand activity we noticed:
{recent_activity_summary}

Our value proposition:
{opportunity_angle}

Requirements:
- Subject line: specific, relevant, under 60 characters
- Body: 3 short paragraphs (opener referencing their activity, value prop, CTA for a 15-min call)
- Tone: confident but not pushy
- Do NOT fabricate statistics or claims not in the provided data

Return in this exact format (no extra text before or after):
Subject: <subject line>
Body:
<email body>
"""
