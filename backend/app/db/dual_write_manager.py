"""
Dual-Write Manager
Writes to both PostgreSQL and JSON for safe migration
Reads from PostgreSQL first, falls back to JSON
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from .models import IntelligenceReport
from .session import get_db, is_db_available
from app.intelligence.models import CompanyIntelligence

logger = logging.getLogger(__name__)


class DualWriteManager:
    """
    Manages dual-write pattern for safe migration
    - Writes to both PostgreSQL and JSON
    - Reads from PostgreSQL first, falls back to JSON
    - Graceful degradation if PostgreSQL unavailable
    """
    
    def __init__(self):
        self.json_dir = Path("data/intelligence_reports")
        self.json_dir.mkdir(parents=True, exist_ok=True)
        self.db_available = is_db_available()
        
        if self.db_available:
            logger.info("✅ Dual-write mode: PostgreSQL + JSON")
        else:
            logger.info("⚠️  JSON-only mode: PostgreSQL unavailable")
    
    def save_intelligence_report(
        self,
        company_name: str,
        intelligence: CompanyIntelligence,
        user_id: Optional[int] = None
    ) -> bool:
        """
        Save intelligence report to both PostgreSQL and JSON
        Returns True if at least one save succeeded
        """
        json_success = self._save_to_json(company_name, intelligence)
        pg_success = False
        
        if self.db_available:
            pg_success = self._save_to_postgres(company_name, intelligence, user_id)
        
        if json_success or pg_success:
            logger.info(f"✅ Saved intelligence for {company_name} (JSON: {json_success}, PG: {pg_success})")
            return True
        else:
            logger.error(f"❌ Failed to save intelligence for {company_name}")
            return False
    
    def load_intelligence_report(
        self,
        company_name: str,
        max_age_hours: int = 24
    ) -> Optional[CompanyIntelligence]:
        """
        Load intelligence report
        Try PostgreSQL first, fall back to JSON
        """
        # Try PostgreSQL first
        if self.db_available:
            report = self._load_from_postgres(company_name, max_age_hours)
            if report:
                logger.debug(f"⚡ Loaded {company_name} from PostgreSQL")
                return report
        
        # Fall back to JSON
        report = self._load_from_json(company_name, max_age_hours)
        if report:
            logger.debug(f"⚡ Loaded {company_name} from JSON")
            return report
        
        logger.debug(f"❌ No cached report found for {company_name}")
        return None
    
    def _save_to_json(
        self,
        company_name: str,
        intelligence: CompanyIntelligence
    ) -> bool:
        """Save to JSON file"""
        try:
            filename = self._get_json_filename(company_name)
            filepath = self.json_dir / filename
            
            # Convert to dict
            data = intelligence.dict()
            data['generated_at'] = data['generated_at'].isoformat()
            
            # Write to file
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"JSON save error: {e}")
            return False
    
    def _save_to_postgres(
        self,
        company_name: str,
        intelligence: CompanyIntelligence,
        user_id: Optional[int] = None
    ) -> bool:
        """Save to PostgreSQL"""
        try:
            db_gen = get_db()
            db = next(db_gen)
            
            if db is None:
                return False
            
            try:
                # Check if report exists
                existing = db.query(IntelligenceReport).filter(
                    IntelligenceReport.company_name == company_name
                ).first()
                
                if existing:
                    # Update existing
                    existing.category = intelligence.category
                    existing.business_model = intelligence.business_model
                    existing.positioning = intelligence.positioning
                    existing.scale_metrics = intelligence.scale_metrics
                    existing.brand_perception = intelligence.brand_perception
                    existing.recent_shifts = intelligence.recent_shifts
                    existing.competitors = intelligence.competitors
                    existing.activities = intelligence.activities
                    existing.events = intelligence.events
                    existing.watchouts = intelligence.watchouts
                    existing.decision_makers = intelligence.decision_makers
                    existing.outreach_messages = intelligence.outreach_messages
                    existing.confidence_score = intelligence.confidence_score
                    existing.generated_at = intelligence.generated_at
                    existing.updated_at = datetime.now()
                else:
                    # Create new
                    report = IntelligenceReport(
                        user_id=user_id,
                        company_name=company_name,
                        category=intelligence.category,
                        business_model=intelligence.business_model,
                        positioning=intelligence.positioning,
                        scale_metrics=intelligence.scale_metrics,
                        brand_perception=intelligence.brand_perception,
                        recent_shifts=intelligence.recent_shifts,
                        competitors=intelligence.competitors,
                        activities=intelligence.activities,
                        events=intelligence.events,
                        watchouts=intelligence.watchouts,
                        decision_makers=intelligence.decision_makers,
                        outreach_messages=intelligence.outreach_messages,
                        confidence_score=intelligence.confidence_score,
                        generated_at=intelligence.generated_at
                    )
                    db.add(report)
                
                db.commit()
                return True
                
            finally:
                next(db_gen, None)
        
        except Exception as e:
            logger.error(f"PostgreSQL save error: {e}")
            return False
    
    def _load_from_json(
        self,
        company_name: str,
        max_age_hours: int = 24
    ) -> Optional[CompanyIntelligence]:
        """Load from JSON file"""
        try:
            filename = self._get_json_filename(company_name)
            filepath = self.json_dir / filename
            
            if not filepath.exists():
                return None
            
            # Check age
            file_age_hours = (datetime.now().timestamp() - filepath.stat().st_mtime) / 3600
            if file_age_hours > max_age_hours:
                logger.debug(f"JSON file too old: {file_age_hours:.1f}h > {max_age_hours}h")
                return None
            
            # Load data
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Convert datetime
            data['generated_at'] = datetime.fromisoformat(data['generated_at'])
            
            return CompanyIntelligence(**data)
        
        except Exception as e:
            logger.error(f"JSON load error: {e}")
            return None
    
    def _load_from_postgres(
        self,
        company_name: str,
        max_age_hours: int = 24
    ) -> Optional[CompanyIntelligence]:
        """Load from PostgreSQL"""
        try:
            db_gen = get_db()
            db = next(db_gen)
            
            if db is None:
                return None
            
            try:
                # Query report
                report = db.query(IntelligenceReport).filter(
                    IntelligenceReport.company_name == company_name
                ).order_by(IntelligenceReport.created_at.desc()).first()
                
                if not report:
                    return None
                
                # Check age
                age_hours = (datetime.now() - report.created_at).total_seconds() / 3600
                if age_hours > max_age_hours:
                    logger.debug(f"PostgreSQL report too old: {age_hours:.1f}h > {max_age_hours}h")
                    return None
                
                # Convert to CompanyIntelligence
                return CompanyIntelligence(
                    company_name=report.company_name,
                    category=report.category,
                    business_model=report.business_model,
                    positioning=report.positioning,
                    scale_metrics=report.scale_metrics,
                    brand_perception=report.brand_perception,
                    recent_shifts=report.recent_shifts,
                    competitors=report.competitors,
                    activities=report.activities,
                    events=report.events,
                    watchouts=report.watchouts,
                    decision_makers=report.decision_makers,
                    outreach_messages=report.outreach_messages,
                    confidence_score=float(report.confidence_score) if report.confidence_score else 0.0,
                    generated_at=report.generated_at
                )
            
            finally:
                next(db_gen, None)
        
        except Exception as e:
            logger.error(f"PostgreSQL load error: {e}")
            return None
    
    def _get_json_filename(self, company_name: str) -> str:
        """Generate JSON filename from company name"""
        safe_name = company_name.lower().replace(" ", "_").replace("/", "_")
        return f"{safe_name}_intelligence.json"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        stats = {
            "json_enabled": True,
            "postgres_enabled": self.db_available,
            "json_reports": len(list(self.json_dir.glob("*.json")))
        }
        
        if self.db_available:
            try:
                db_gen = get_db()
                db = next(db_gen)
                if db:
                    try:
                        count = db.query(IntelligenceReport).count()
                        stats["postgres_reports"] = count
                    finally:
                        next(db_gen, None)
            except Exception as e:
                stats["postgres_error"] = str(e)
        
        return stats


# Global instance
dual_write_manager = DualWriteManager()
