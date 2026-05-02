"""
Outreach Generator Module
Generates personalized outreach messages using LLM
"""
import os
from typing import Dict, List
from groq import Groq
from .models import OutreachMessage, DecisionMaker, CompanyIntelligence


class OutreachGenerator:
    """Generate personalized outreach messages"""
    
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.groq_client = Groq(api_key=self.groq_key) if self.groq_key else None
    
    def generate_outreach(
        self,
        decision_maker: DecisionMaker,
        intelligence: CompanyIntelligence,
        opportunity_angle: str = "marketing technology partnership"
    ) -> Dict[str, OutreachMessage]:
        """
        Generate personalized outreach messages for email and LinkedIn
        """
        messages = {}
        
        # Generate LinkedIn message
        linkedin_msg = self._generate_linkedin_message(
            decision_maker, intelligence, opportunity_angle
        )
        messages["linkedin"] = linkedin_msg
        
        # Generate email
        email_msg = self._generate_email(
            decision_maker, intelligence, opportunity_angle
        )
        messages["email"] = email_msg
        
        return messages
    
    def _generate_linkedin_message(
        self,
        decision_maker: DecisionMaker,
        intelligence: CompanyIntelligence,
        opportunity_angle: str
    ) -> OutreachMessage:
        """Generate LinkedIn connection message"""
        if not self.groq_client:
            return OutreachMessage(
                channel="linkedin",
                message=f"Hi {decision_maker.name.split()[0]}, I'd love to connect and discuss opportunities in {intelligence.category}.",
                personalization_notes=["Generic message - LLM unavailable"]
            )
        
        try:
            # Prepare context
            recent_activity = intelligence.activities[0].title if intelligence.activities else "recent initiatives"
            
            prompt = f"""Write a personalized LinkedIn connection request message.

RECIPIENT:
Name: {decision_maker.name}
Title: {decision_maker.title}
Company: {intelligence.company_name}

COMPANY CONTEXT:
Industry: {intelligence.category}
Recent Activity: {recent_activity}
Positioning: {intelligence.positioning[:150]}

OPPORTUNITY: {opportunity_angle}

REQUIREMENTS:
- Maximum 300 characters (LinkedIn limit)
- Mention their company or recent activity
- Be professional but warm
- Clear value proposition
- No hard sell

Write only the message, no subject line."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            
            message = response.choices[0].message.content.strip()
            
            # Ensure it's not too long
            if len(message) > 300:
                message = message[:297] + "..."
            
            return OutreachMessage(
                channel="linkedin",
                message=message,
                personalization_notes=[
                    f"Referenced: {intelligence.company_name}",
                    f"Context: {recent_activity[:50]}",
                    f"Angle: {opportunity_angle}"
                ]
            )
            
        except Exception as e:
            print(f"Error generating LinkedIn message: {e}")
            return OutreachMessage(
                channel="linkedin",
                message=f"Hi {decision_maker.name.split()[0]}, impressed by {intelligence.company_name}'s work in {intelligence.category}. Would love to connect!",
                personalization_notes=["Fallback message"]
            )
    
    def _generate_email(
        self,
        decision_maker: DecisionMaker,
        intelligence: CompanyIntelligence,
        opportunity_angle: str
    ) -> OutreachMessage:
        """Generate personalized email"""
        if not self.groq_client:
            return OutreachMessage(
                channel="email",
                subject=f"Opportunity for {intelligence.company_name}",
                message=f"Dear {decision_maker.name},\n\nI wanted to reach out regarding potential opportunities in {intelligence.category}.\n\nBest regards",
                personalization_notes=["Generic email - LLM unavailable"]
            )
        
        try:
            # Prepare context
            recent_activities = "\n".join([
                f"- {activity.title}"
                for activity in intelligence.activities[:3]
            ]) if intelligence.activities else "recent company initiatives"
            
            competitors_context = ", ".join([
                comp.name for comp in intelligence.competitors[:3]
            ]) if intelligence.competitors else "industry peers"
            
            prompt = f"""Write a personalized cold outreach email.

RECIPIENT:
Name: {decision_maker.name}
Title: {decision_maker.title}
Company: {intelligence.company_name}

COMPANY INTELLIGENCE:
Industry: {intelligence.category}
Positioning: {intelligence.positioning[:200]}
Recent Activities:
{recent_activities}
Competitors: {competitors_context}

OPPORTUNITY: {opportunity_angle}

EMAIL REQUIREMENTS:
1. Compelling subject line (under 60 characters)
2. Personalized opening referencing their company or recent activity
3. Clear value proposition
4. Demonstrate research and understanding
5. Soft call-to-action
6. Professional but conversational tone
7. Keep email under 150 words

FORMAT:
SUBJECT: [subject line]

[email body]

Return both subject and body."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse subject and body
            subject = ""
            body = content
            
            if "SUBJECT:" in content:
                parts = content.split("\n", 1)
                subject = parts[0].replace("SUBJECT:", "").strip()
                body = parts[1].strip() if len(parts) > 1 else content
            
            return OutreachMessage(
                channel="email",
                subject=subject or f"Quick question about {intelligence.company_name}",
                message=body,
                personalization_notes=[
                    f"Referenced: {intelligence.company_name}",
                    f"Recent activity: {intelligence.activities[0].title[:50] if intelligence.activities else 'N/A'}",
                    f"Competitors mentioned: {competitors_context}",
                    f"Angle: {opportunity_angle}"
                ]
            )
            
        except Exception as e:
            print(f"Error generating email: {e}")
            first_name = decision_maker.name.split()[0]
            return OutreachMessage(
                channel="email",
                subject=f"Opportunity for {intelligence.company_name}",
                message=f"Hi {first_name},\n\nI've been following {intelligence.company_name}'s work in {intelligence.category} and wanted to reach out about potential collaboration opportunities.\n\nWould you be open to a brief conversation?\n\nBest regards",
                personalization_notes=["Fallback email"]
            )
