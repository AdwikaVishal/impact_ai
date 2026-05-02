"""
Intelligence API Endpoints
Market Intelligence Engine for brand research and outreach
Supports both synchronous and asynchronous processing
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
import uuid
from datetime import datetime

from app.intelligence.models import CompanyInput, CompanyIntelligence
from app.intelligence.orchestrator import IntelligenceOrchestrator
from app.core.cache import cache
from app.core.feature_flags import feature_flags
from app.core.celery_app import is_celery_available
from app.db.dual_write_manager import dual_write_manager

router = APIRouter()
orchestrator = IntelligenceOrchestrator()

# Task storage (in-memory for now, could use Redis)
tasks = {}


@router.post("/analyze", response_model=CompanyIntelligence)
async def analyze_company(
    company_input: CompanyInput,
    opportunity_angle: str = "marketing technology partnership"
):
    """
    Generate comprehensive intelligence report (SYNCHRONOUS)
    
    **Input:**
    - company_name: Company name
    - category: One-line category/industry
    - opportunity_angle: (optional) Angle for outreach personalization
    
    **Output:**
    - Complete intelligence report including:
      1. Company Overview (business model, positioning, scale)
      2. Market Position (brand perception, recent shifts)
      3. Competitor Mapping (3-5 competitors with analysis)
      4. Brand Activity (campaigns, launches, timeline)
      5. Events Footprint (events, activations)
      6. Strategic Watchouts (risks, tensions, blind spots)
      7. Decision Makers (relevant stakeholders with roles)
      8. Contact Intelligence (emails, phones, LinkedIn)
      9. Personalized Outreach (LinkedIn + email messages)
      10. Metadata (confidence score, generation timestamp)
    """
    try:
        intelligence = await orchestrator.generate_intelligence(
            company_input,
            opportunity_angle
        )
        
        # Save to dual-write storage
        dual_write_manager.save_intelligence_report(
            company_input.company_name,
            intelligence
        )
        
        return intelligence
        
    except Exception as e:
        print(f"Error generating intelligence: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate intelligence: {str(e)}"
        )


@router.post("/analyze/async", status_code=202)
async def analyze_company_async(
    company_input: CompanyInput,
    opportunity_angle: str = "marketing technology partnership",
    background_tasks: BackgroundTasks = None
):
    """
    Generate intelligence report ASYNCHRONOUSLY
    
    Returns immediately with task_id for status checking.
    Use /analyze/status/{task_id} to check progress.
    
    **Requires:** Celery workers running (optional)
    **Fallback:** Uses BackgroundTasks if Celery unavailable
    """
    task_id = str(uuid.uuid4())
    
    # Try Celery first
    if is_celery_available():
        try:
            from app.workers.intelligence_tasks import generate_intelligence_async
            
            result = generate_intelligence_async.apply_async(
                args=[
                    company_input.company_name,
                    company_input.category,
                    opportunity_angle
                ]
            )
            
            tasks[task_id] = {
                "task_id": task_id,
                "celery_task_id": result.id,
                "company_name": company_input.company_name,
                "status": "queued",
                "created_at": datetime.now().isoformat(),
                "backend": "celery"
            }
            
            return {
                "task_id": task_id,
                "status": "queued",
                "status_url": f"/api/v1/intelligence/analyze/status/{task_id}",
                "backend": "celery"
            }
        
        except Exception as e:
            print(f"Celery task failed: {e}, falling back to BackgroundTasks")
    
    # Fallback to FastAPI BackgroundTasks
    if background_tasks:
        tasks[task_id] = {
            "task_id": task_id,
            "company_name": company_input.company_name,
            "status": "processing",
            "created_at": datetime.now().isoformat(),
            "backend": "background_tasks"
        }
        
        background_tasks.add_task(
            _run_intelligence_background,
            task_id,
            company_input,
            opportunity_angle
        )
        
        return {
            "task_id": task_id,
            "status": "processing",
            "status_url": f"/api/v1/intelligence/analyze/status/{task_id}",
            "backend": "background_tasks"
        }
    
    # No async available
    raise HTTPException(
        status_code=503,
        detail="Async processing not available. Use /analyze endpoint instead."
    )


async def _run_intelligence_background(
    task_id: str,
    company_input: CompanyInput,
    opportunity_angle: str
):
    """Background task runner for FastAPI BackgroundTasks"""
    try:
        intelligence = await orchestrator.generate_intelligence(
            company_input,
            opportunity_angle
        )
        
        # Save to storage
        dual_write_manager.save_intelligence_report(
            company_input.company_name,
            intelligence
        )
        
        # Update task status
        result = intelligence.dict()
        result['generated_at'] = result['generated_at'].isoformat()
        
        tasks[task_id].update({
            "status": "completed",
            "data": result,
            "completed_at": datetime.now().isoformat()
        })
    
    except Exception as e:
        tasks[task_id].update({
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        })


@router.get("/analyze/status/{task_id}")
async def get_task_status(task_id: str):
    """
    Check status of async intelligence generation task
    
    **Returns:**
    - status: queued, processing, completed, or failed
    - data: intelligence report (if completed)
    - error: error message (if failed)
    """
    task = tasks.get(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # If using Celery, check Celery task status
    if task.get("backend") == "celery" and is_celery_available():
        try:
            from app.core.celery_app import celery_app
            celery_task_id = task.get("celery_task_id")
            
            if celery_task_id:
                result = celery_app.AsyncResult(celery_task_id)
                
                if result.ready():
                    if result.successful():
                        task_result = result.get()
                        task.update({
                            "status": "completed",
                            "data": task_result.get("data"),
                            "completed_at": task_result.get("completed_at")
                        })
                    else:
                        task.update({
                            "status": "failed",
                            "error": str(result.info),
                            "failed_at": datetime.now().isoformat()
                        })
                else:
                    task["status"] = result.state.lower()
        
        except Exception as e:
            print(f"Error checking Celery task: {e}")
    
    return task


@router.post("/analyze/batch", status_code=202)
async def analyze_batch(
    companies: list,
    opportunity_angle: str = "marketing technology partnership"
):
    """
    Generate intelligence for multiple companies asynchronously
    
    **Requires:** Celery workers running
    **Input:** List of {company_name, category} objects
    """
    if not is_celery_available():
        raise HTTPException(
            status_code=503,
            detail="Batch processing requires Celery. Use individual /analyze endpoint instead."
        )
    
    try:
        from app.workers.intelligence_tasks import batch_generate_intelligence
        
        result = batch_generate_intelligence.apply_async(
            args=[companies, opportunity_angle]
        )
        
        return {
            "batch_id": result.id,
            "total": len(companies),
            "status": "queued",
            "status_url": f"/api/v1/intelligence/analyze/batch/status/{result.id}"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Batch processing failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint with cache, database, and Celery status"""
    cache_stats = cache.get_stats()
    
    # Check database status
    from app.db.session import is_db_available
    from app.db.dual_write_manager import dual_write_manager
    
    db_status = {
        "enabled": is_db_available(),
        "dual_write": is_db_available()
    }
    
    if is_db_available():
        try:
            db_stats = dual_write_manager.get_stats()
            db_status.update(db_stats)
        except Exception as e:
            db_status["error"] = str(e)
    
    # Check Celery status
    from app.core.celery_app import is_celery_available
    
    celery_status = {
        "enabled": is_celery_available(),
        "async_endpoints": is_celery_available()
    }
    
    return {
        "status": "healthy",
        "service": "Market Intelligence Engine",
        "version": "3.0.0",
        "features": feature_flags.get_all(),
        "cache": cache_stats,
        "database": db_status,
        "celery": celery_status
    }


@router.get("/cache/stats")
async def cache_statistics():
    """Get detailed cache statistics"""
    if not cache.enabled:
        return {
            "enabled": False,
            "message": "Cache is not enabled"
        }
    
    stats = cache.get_stats()
    return {
        "enabled": True,
        "statistics": stats,
        "ttls": {
            "intelligence_report": "24 hours",
            "company_profile": "48 hours",
            "competitors": "72 hours",
            "decision_makers": "7 days",
            "news": "6 hours",
            "events": "30 days"
        }
    }


@router.post("/cache/clear")
async def clear_cache(pattern: str = "*"):
    """Clear cache by pattern (use with caution)"""
    if not cache.enabled:
        return {
            "success": False,
            "message": "Cache is not enabled"
        }
    
    try:
        cache.clear_pattern(pattern)
        return {
            "success": True,
            "message": f"Cache cleared for pattern: {pattern}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear cache: {str(e)}"
        )
