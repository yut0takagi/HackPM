import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

# Import our modules
from database import create_tables, get_db, Repository, Branch, PullRequest, Issue, CIRun, Event
from github_webhook import webhook_handler
from github_api import github_api

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Background tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting hack-pm backend...")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created/verified")
    
    # Start background scheduler
    scheduler.start()
    
    # Schedule GitHub API sync every 10 minutes
    scheduler.add_job(
        sync_github_data,
        IntervalTrigger(minutes=10),
        id="github_sync",
        replace_existing=True
    )
    logger.info("Background scheduler started")
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    logger.info("Background scheduler stopped")

app = FastAPI(
    title="Hack PM - GitHub Integration Hub", 
    version="1.0.0",
    description="Real-time GitHub repository monitoring and project management dashboard",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://frontend:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def sync_github_data():
    """Background task to sync GitHub data"""
    try:
        logger.info("Starting GitHub data sync...")
        db = next(get_db())
        await github_api.sync_repositories(db)
        logger.info("GitHub data sync completed")
    except Exception as e:
        logger.error(f"GitHub data sync failed: {e}")
    finally:
        db.close()

# Pydantic models
class WebhookPayload(BaseModel):
    pass  # Will accept any JSON payload

class NotificationRequest(BaseModel):
    message: str
    webhook_url: Optional[str] = None

class RepoStatsResponse(BaseModel):
    total_repos: int
    total_branches: int
    open_prs: int
    open_issues: int
    recent_ci_runs: int

@app.get("/")
async def root():
    return {
        "message": "Hack PM - GitHub Integration Hub",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

# GitHub Webhook endpoint
@app.post("/api/github/webhook")
async def github_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle GitHub webhooks"""
    return await webhook_handler.handle_webhook(request, db)

# Repository endpoints
@app.get("/api/repos")
async def get_repositories(db: Session = Depends(get_db)):
    """Get all monitored repositories"""
    repos = db.query(Repository).order_by(desc(Repository.updated_at)).all()
    
    result = []
    for repo in repos:
        # Get latest stats
        branch_count = db.query(Branch).filter(Branch.repo_id == repo.id).count()
        open_prs = db.query(PullRequest).filter(
            and_(PullRequest.repo_id == repo.id, PullRequest.state == "open")
        ).count()
        open_issues = db.query(Issue).filter(
            and_(Issue.repo_id == repo.id, Issue.state == "open")
        ).count()
        
        # Get latest CI status
        latest_ci = db.query(CIRun).filter(CIRun.repo_id == repo.id).order_by(desc(CIRun.updated_at)).first()
        
        result.append({
            "id": repo.id,
            "full_name": repo.full_name,
            "name": repo.name,
            "owner": repo.owner,
            "description": repo.description,
            "html_url": repo.html_url,
            "default_branch": repo.default_branch,
            "visibility": repo.visibility,
            "updated_at": repo.updated_at.isoformat() if repo.updated_at else None,
            "stats": {
                "branches": branch_count,
                "open_prs": open_prs,
                "open_issues": open_issues,
                "latest_ci_status": latest_ci.status if latest_ci else None,
                "latest_ci_conclusion": latest_ci.conclusion if latest_ci else None
            }
        })
    
    return result

@app.get("/api/repos/{repo_id}")
async def get_repository(repo_id: int, db: Session = Depends(get_db)):
    """Get repository details"""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return {
        "id": repo.id,
        "full_name": repo.full_name,
        "name": repo.name,
        "owner": repo.owner,
        "description": repo.description,
        "html_url": repo.html_url,
        "clone_url": repo.clone_url,
        "ssh_url": repo.ssh_url,
        "default_branch": repo.default_branch,
        "visibility": repo.visibility,
        "created_at": repo.created_at.isoformat() if repo.created_at else None,
        "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
    }

@app.get("/api/repos/{repo_id}/branches")
async def get_repository_branches(
    repo_id: int, 
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Get repository branches"""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    branches = db.query(Branch).filter(Branch.repo_id == repo_id).order_by(
        desc(Branch.is_default), desc(Branch.updated_at)
    ).limit(limit).all()
    
    return [
        {
            "id": branch.id,
            "name": branch.name,
            "head_sha": branch.head_sha,
            "is_default": branch.is_default,
            "is_protected": branch.is_protected,
            "last_commit_message": branch.last_commit_message,
            "last_commit_author": branch.last_commit_author,
            "last_commit_date": branch.last_commit_date.isoformat() if branch.last_commit_date else None,
            "pushed_at": branch.pushed_at.isoformat() if branch.pushed_at else None,
            "updated_at": branch.updated_at.isoformat() if branch.updated_at else None
        }
        for branch in branches
    ]

@app.get("/api/repos/{repo_id}/pulls")
async def get_repository_pulls(
    repo_id: int,
    state: str = Query("open", regex="^(open|closed|all)$"),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Get repository pull requests"""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    query = db.query(PullRequest).filter(PullRequest.repo_id == repo_id)
    
    if state != "all":
        query = query.filter(PullRequest.state == state)
    
    pulls = query.order_by(desc(PullRequest.updated_at)).limit(limit).all()
    
    return [
        {
            "id": pr.id,
            "number": pr.number,
            "title": pr.title,
            "body": pr.body,
            "author": pr.author,
            "author_avatar": pr.author_avatar,
            "state": pr.state,
            "draft": pr.draft,
            "head_ref": pr.head_ref,
            "base_ref": pr.base_ref,
            "head_sha": pr.head_sha,
            "html_url": pr.html_url,
            "mergeable": pr.mergeable,
            "merged_at": pr.merged_at.isoformat() if pr.merged_at else None,
            "closed_at": pr.closed_at.isoformat() if pr.closed_at else None,
            "created_at": pr.created_at.isoformat() if pr.created_at else None,
            "updated_at": pr.updated_at.isoformat() if pr.updated_at else None
        }
        for pr in pulls
    ]

@app.get("/api/repos/{repo_id}/issues")
async def get_repository_issues(
    repo_id: int,
    state: str = Query("open", regex="^(open|closed|all)$"),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Get repository issues"""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    query = db.query(Issue).filter(Issue.repo_id == repo_id)
    
    if state != "all":
        query = query.filter(Issue.state == state)
    
    issues = query.order_by(desc(Issue.updated_at)).limit(limit).all()
    
    return [
        {
            "id": issue.id,
            "number": issue.number,
            "title": issue.title,
            "body": issue.body,
            "author": issue.author,
            "author_avatar": issue.author_avatar,
            "state": issue.state,
            "labels": json.loads(issue.labels_json) if issue.labels_json else [],
            "assignees": json.loads(issue.assignees_json) if issue.assignees_json else [],
            "milestone": issue.milestone,
            "html_url": issue.html_url,
            "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
            "created_at": issue.created_at.isoformat() if issue.created_at else None,
            "updated_at": issue.updated_at.isoformat() if issue.updated_at else None
        }
        for issue in issues
    ]

@app.get("/api/repos/{repo_id}/ci-runs")
async def get_repository_ci_runs(
    repo_id: int,
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Get repository CI runs"""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    ci_runs = db.query(CIRun).filter(CIRun.repo_id == repo_id).order_by(
        desc(CIRun.updated_at)
    ).limit(limit).all()
    
    return [
        {
            "id": run.id,
            "run_id": run.run_id,
            "workflow_name": run.workflow_name,
            "status": run.status,
            "conclusion": run.conclusion,
            "head_branch": run.head_branch,
            "head_sha": run.head_sha,
            "event": run.event,
            "actor": run.actor,
            "html_url": run.html_url,
            "run_started_at": run.run_started_at.isoformat() if run.run_started_at else None,
            "run_updated_at": run.run_updated_at.isoformat() if run.run_updated_at else None,
            "updated_at": run.updated_at.isoformat() if run.updated_at else None
        }
        for run in ci_runs
    ]

@app.get("/api/events")
async def get_events(
    repo: Optional[str] = Query(None, description="Repository full name filter"),
    event_type: Optional[str] = Query(None, description="Event type filter"),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """Get recent events"""
    query = db.query(Event).join(Repository)
    
    if repo:
        query = query.filter(Repository.full_name == repo)
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    events = query.order_by(desc(Event.created_at)).limit(limit).all()
    
    return [
        {
            "id": event.id,
            "repository": event.repository.full_name,
            "event_type": event.event_type,
            "action": event.action,
            "actor": event.actor,
            "ref": event.ref,
            "delivery_id": event.delivery_id,
            "created_at": event.created_at.isoformat() if event.created_at else None
        }
        for event in events
    ]

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get overall statistics"""
    total_repos = db.query(Repository).count()
    total_branches = db.query(Branch).count()
    open_prs = db.query(PullRequest).filter(PullRequest.state == "open").count()
    open_issues = db.query(Issue).filter(Issue.state == "open").count()
    
    # Recent CI runs (last 24 hours)
    yesterday = datetime.utcnow() - timedelta(days=1)
    recent_ci_runs = db.query(CIRun).filter(CIRun.updated_at >= yesterday).count()
    
    # Recent events (last 24 hours)
    recent_events = db.query(Event).filter(Event.created_at >= yesterday).count()
    
    return {
        "total_repos": total_repos,
        "total_branches": total_branches,
        "open_prs": open_prs,
        "open_issues": open_issues,
        "recent_ci_runs": recent_ci_runs,
        "recent_events": recent_events,
        "last_updated": datetime.utcnow().isoformat()
    }

# Additional endpoints for Discord notifications and manual sync
@app.post("/api/discord/notify")
async def send_discord_notification(notification: NotificationRequest):
    """Send Discord notification"""
    try:
        import httpx
        webhook_url = notification.webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
        
        if not webhook_url:
            raise HTTPException(status_code=400, detail="Discord webhook URL not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                webhook_url,
                json={"content": notification.message},
                timeout=10.0
            )
            
        if response.status_code == 204:
            return {"message": "Notification sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send notification")
            
    except Exception as e:
        logger.error(f"Discord notification error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")

@app.post("/api/sync/github")
async def manual_github_sync(db: Session = Depends(get_db)):
    """Manually trigger GitHub data sync"""
    try:
        await github_api.sync_repositories(db)
        return {"message": "GitHub sync completed successfully"}
    except Exception as e:
        logger.error(f"Manual sync error: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@app.get("/api/export/events")
async def export_events(
    format: str = Query("json", regex="^(json|csv)$"),
    repo: Optional[str] = Query(None),
    days: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Export events data"""
    try:
        from datetime import timedelta
        import csv
        import io
        
        # Get events from last N days
        since = datetime.utcnow() - timedelta(days=days)
        query = db.query(Event).join(Repository).filter(Event.created_at >= since)
        
        if repo:
            query = query.filter(Repository.full_name == repo)
        
        events = query.order_by(desc(Event.created_at)).all()
        
        if format == "json":
            return [
                {
                    "id": event.id,
                    "repository": event.repository.full_name,
                    "event_type": event.event_type,
                    "action": event.action,
                    "actor": event.actor,
                    "ref": event.ref,
                    "delivery_id": event.delivery_id,
                    "created_at": event.created_at.isoformat() if event.created_at else None
                }
                for event in events
            ]
        
        elif format == "csv":
            from fastapi.responses import StreamingResponse
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                "ID", "Repository", "Event Type", "Action", "Actor", 
                "Ref", "Delivery ID", "Created At"
            ])
            
            # Write data
            for event in events:
                writer.writerow([
                    event.id,
                    event.repository.full_name,
                    event.event_type,
                    event.action or "",
                    event.actor or "",
                    event.ref or "",
                    event.delivery_id or "",
                    event.created_at.isoformat() if event.created_at else ""
                ])
            
            output.seek(0)
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=events.csv"}
            )
            
    except Exception as e:
        logger.error(f"Export error: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)