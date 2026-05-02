"""
Celery Tasks for Intelligence Generation
Background processing of intelligence reports
"""
from typing import Dict, Any
import logging
from datetime import datetime

from app.core.celery_app import celery_app, is_celery_available
from app.intelligence.models import CompanyInput
from app.intelligence.orchestrator import IntelligenceOrchestrator
from app.db.dual_write_manager import dual_write_manager

logger = logging.getLogger(__name__)


if is_celery_available() and celery_app:
    
    @celery_app.task(name="generate_intelligence_async", bind=True)
    def generate_intelligence_async(
        self,
        company_name: str,
        category: str,
        opportunity_angle: str = "marketing technology partnership",
        user_id: int = None
    ) -> Dict[str, Any]:
        """
        Generate intelligence report asynchronously
        
        Args:
            company_name: Company name
            category: Company category/industry
            opportunity_angle: Outreach angle
            user_id: Optional user ID
        
        Returns:
            Dict with intelligence data or error
        """
        try:
            # Update task state
            self.update_state(
                state='PROCESSING',
                meta={
                    'company_name': company_name,
                    'status': 'Generating intelligence report...',
                    'progress': 0
                }
            )
            
            # Create orchestrator
            orchestrator = IntelligenceOrchestrator()
            
            # Generate intelligence
            company_input = CompanyInput(
                company_name=company_name,
                category=category
            )
            
            # This is async in the orchestrator
            import asyncio
            intelligence = asyncio.run(
                orchestrator.generate_intelligence(
                    company_input,
                    opportunity_angle
                )
            )
            
            # Save to dual-write storage
            dual_write_manager.save_intelligence_report(
                company_name,
                intelligence,
                user_id
            )
            
            # Convert to dict for return
            result = intelligence.dict()
            result['generated_at'] = result['generated_at'].isoformat()
            
            return {
                'status': 'completed',
                'company_name': company_name,
                'data': result,
                'completed_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Intelligence generation failed: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'status': 'failed',
                'company_name': company_name,
                'error': str(e),
                'failed_at': datetime.now().isoformat()
            }
    
    
    @celery_app.task(name="batch_generate_intelligence")
    def batch_generate_intelligence(
        companies: list,
        opportunity_angle: str = "marketing technology partnership"
    ) -> Dict[str, Any]:
        """
        Generate intelligence for multiple companies
        
        Args:
            companies: List of dicts with company_name and category
            opportunity_angle: Outreach angle
        
        Returns:
            Dict with batch results
        """
        results = []
        
        for company in companies:
            try:
                result = generate_intelligence_async.apply_async(
                    args=[
                        company['company_name'],
                        company['category'],
                        opportunity_angle
                    ]
                )
                results.append({
                    'company_name': company['company_name'],
                    'task_id': result.id,
                    'status': 'queued'
                })
            except Exception as e:
                results.append({
                    'company_name': company['company_name'],
                    'status': 'failed',
                    'error': str(e)
                })
        
        return {
            'batch_id': datetime.now().isoformat(),
            'total': len(companies),
            'results': results
        }

else:
    # Celery not available - provide stub functions
    logger.warning("⚠️  Celery tasks not available - using synchronous fallback")
    
    def generate_intelligence_async(*args, **kwargs):
        raise RuntimeError("Celery not available - use synchronous endpoint")
    
    def batch_generate_intelligence(*args, **kwargs):
        raise RuntimeError("Celery not available - use synchronous endpoint")
