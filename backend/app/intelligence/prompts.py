"""
prompts.py – All LLM prompt templates for the intelligence layer.

Each template uses Python .format() placeholders.
"""

# ---------------------------------------------------------------------------
# Output #1 – Company Overview
# ---------------------------------------------------------------------------

OVERVIEW_PROMPT = """\
You are a market research analyst. Based on the following company's "About" text, \
write a concise company overview (3-4 sentences) covering:

1. Business model (how they make money)
2. Scale (revenue/employees only if explicitly mentioned)
3. Market positioning (premium / mass-market / innovator / challenger / etc.)

About text:
{about_text}

Return ONLY the overview as plain text. No bullet points, no headers, no extra commentary.
If the text is insufficient, respond with exactly: "Insufficient data to generate overview."
"""

# ---------------------------------------------------------------------------
# Output #2 – Market Position
# ---------------------------------------------------------------------------

MARKET_POSITION_PROMPT = """\
Based on the recent news headlines about {company_name} listed below, \
write 2-3 sentences describing:

1. Current brand perception (positive / negative / mixed)
2. Any recent shifts in strategy, reputation, or market focus visible in the headlines

News headlines (last 12 months):
{news_list}

Return ONLY the market position analysis as plain text.
If there are no headlines, respond with exactly: "No recent news available to assess market position."
"""

# ---------------------------------------------------------------------------
# Output #3 – Competitor Gap Analysis
# ---------------------------------------------------------------------------

COMPETITOR_GAPS_PROMPT = """\
Company: {company_name}
Category: {category}

Competitors and their recent activity:
{competitors_list}

Analyse each competitor and return a JSON array where each element has exactly these keys:
  "name"     – competitor name
  "strength" – one key competitive strength based on their activity
  "gap"      – one key weakness or gap visible from the data

Example:
[{{"name": "Adidas", "strength": "strong soccer sponsorships", "gap": "limited DTC presence"}}]

Return ONLY the JSON array, no other text. If no data, return [].
"""

# ---------------------------------------------------------------------------
# Output #6 – Strategic Watchouts
# ---------------------------------------------------------------------------

WATCHOUTS_PROMPT = """\
Based on the following data for {company_name}, identify exactly 3 strategic watchouts \
(risks, tensions, or blind spots) that a marketing agency should know BEFORE engaging this brand.

Data:
- Recent news headlines: {news_summary}
- Main competitors: {competitor_summary}
- Recent events: {events_summary}

Return as a JSON array of exactly 3 strings:
["watchout 1", "watchout 2", "watchout 3"]

Base every point strictly on the provided data. Do not invent facts.
Return ONLY the JSON array.
"""

# ---------------------------------------------------------------------------
# Output #9 – LinkedIn Message
# ---------------------------------------------------------------------------

LINKEDIN_PROMPT = """\
Write a short LinkedIn connection message (150-250 characters) to {name}, \
{role} at {company_name}.

Context from their recent brand activity:
{activity_summary}

Rules:
- Professional but warm tone
- Reference ONE specific recent activity from the context
- End with a soft call to action (e.g., "Would love to connect.")
- Return ONLY the message text, no subject line, no quotes, no signature
"""

# ---------------------------------------------------------------------------
# Output #9 – Email Draft
# ---------------------------------------------------------------------------

EMAIL_PROMPT = """\
Write a professional outreach email to {name}, {role} at {company_name}.

Recent brand activity we noticed:
{activity_summary}

Our value proposition: We help brands like {company_name} increase engagement \
and market presence through strategic marketing partnerships.

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

# ---------------------------------------------------------------------------
# Opportunity angle (internal helper for outreach personalisation)
# ---------------------------------------------------------------------------

OPPORTUNITY_ANGLE_PROMPT = """\
In one sentence (max 20 words), describe the most compelling marketing opportunity \
for an agency approaching {company_name} based on this recent activity:
{activity_summary}

Return ONLY the one-sentence opportunity angle.
"""
