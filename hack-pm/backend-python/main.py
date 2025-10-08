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
from src.services.database import create_tables, get_db, Repository, Branch, PullRequest, Issue, CIRun, Event, HackathonTimeBox
from src.api.github_webhook import webhook_handler
from src.api.github_api import github_api
from src.core.template_parser import template_parser
from src.core.status_mapping import status_mapping_service
from src.core.branch_naming import branch_naming_service
from src.services.timebox_service import timebox_service

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

# CORS設定 - より寛容な設定でフロントエンドアクセスを確保
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://frontend:5173",
        "http://0.0.0.0:3000",
        "http://0.0.0.0:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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

def _calculate_time_remaining_percentage(issue: Issue) -> float:
    """Calculate percentage of time remaining for an issue"""
    if not issue.time_box_start or not issue.time_box_end:
        return 0
    
    now = datetime.utcnow()
    total_duration = (issue.time_box_end - issue.time_box_start).total_seconds()
    elapsed_duration = (now - issue.time_box_start).total_seconds()
    
    if total_duration <= 0:
        return 0
    
    remaining_percentage = max(0, (1 - elapsed_duration / total_duration) * 100)
    return min(100, remaining_percentage)

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
        "status": "running",
        "docs": "/docs",
        "health": "/health",
        "api": "/api"
    }

@app.get("/api/test")
async def api_test():
    """Simple test endpoint for frontend connectivity"""
    return {
        "message": "API is working!",
        "timestamp": datetime.utcnow().isoformat(),
        "cors_headers": "enabled"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "cors_enabled": True,
        "endpoints": {
            "api_root": "/api",
            "docs": "/docs",
            "repos": "/api/repos",
            "stats": "/api/stats"
        }
    }

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
    include_template_data: bool = Query(False, description="Include parsed template data"),
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
    
    result = []
    for issue in issues:
        issue_data = {
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
        
        # Add template data if requested
        if include_template_data:
            labels = json.loads(issue.labels_json) if issue.labels_json else []
            assignees = json.loads(issue.assignees_json) if issue.assignees_json else []
            
            # Parse template data
            template_data = template_parser.parse_issue_body(issue.body, labels)
            
            # Prepare timebox data
            timebox_data = {
                'hackathon_phase': issue.hackathon_phase,
                'hours_until_deadline': (issue.deadline - datetime.utcnow()).total_seconds() / 3600 if issue.deadline else None,
                'is_overdue': issue.deadline < datetime.utcnow() if issue.deadline else False,
                'priority_escalated': issue.priority_escalated,
                'time_remaining_percentage': _calculate_time_remaining_percentage(issue) if issue.time_box_start and issue.time_box_end else None
            }
            
            # Map to dashboard data
            dashboard_data = status_mapping_service.map_issue_to_dashboard(
                template_data,
                labels=labels,
                assignees=assignees,
                issue_state=issue.state,
                timebox_data=timebox_data
            )
            
            # Find related branches
            related_branches = branch_naming_service.find_related_branches(db, issue.number, repo_id)
            
            issue_data["template_data"] = {
                "template_type": template_data.template_type.value,
                "priority": template_data.priority.value,
                "estimated_time": template_data.estimated_time,
                "acceptance_criteria": template_data.acceptance_criteria,
                "technical_requirements": template_data.technical_requirements,
                "branch_suggestion": template_data.branch_suggestion,
                "user_story": template_data.user_story
            }
            
            issue_data["dashboard_data"] = {
                "status": dashboard_data.status.value,
                "category": dashboard_data.category.value,
                "priority": dashboard_data.priority.value,
                "progress_percentage": dashboard_data.progress_percentage,
                "estimated_hours": dashboard_data.estimated_hours,
                "acceptance_criteria_total": dashboard_data.acceptance_criteria_total,
                "acceptance_criteria_completed": dashboard_data.acceptance_criteria_completed,
                "has_technical_requirements": dashboard_data.has_technical_requirements,
                "is_time_sensitive": dashboard_data.is_time_sensitive
            }
            
            # Add time-boxed development data
            issue_data["timebox_data"] = {
                "estimated_hours": issue.estimated_hours,
                "deadline": issue.deadline.isoformat() if issue.deadline else None,
                "time_box_start": issue.time_box_start.isoformat() if issue.time_box_start else None,
                "time_box_end": issue.time_box_end.isoformat() if issue.time_box_end else None,
                "priority_escalated": issue.priority_escalated,
                "hackathon_phase": issue.hackathon_phase,
                "hours_until_deadline": (issue.deadline - datetime.utcnow()).total_seconds() / 3600 if issue.deadline else None,
                "is_overdue": issue.deadline < datetime.utcnow() if issue.deadline else False,
                "time_remaining_percentage": _calculate_time_remaining_percentage(issue) if issue.time_box_start and issue.time_box_end else None
            }
            
            issue_data["related_branches"] = [
                {
                    "id": branch.id,
                    "name": branch.name,
                    "head_sha": branch.head_sha,
                    "last_commit_date": branch.last_commit_date.isoformat() if branch.last_commit_date else None
                }
                for branch in related_branches
            ]
        
        result.append(issue_data)
    
    return result

@app.get("/api/repos/{repo_id}/git-graph")
async def get_repository_git_graph(
    repo_id: int,
    limit: int = Query(100, le=200),
    db: Session = Depends(get_db)
):
    """Get repository git graph data (commits, branches, merges)"""
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    # Get branches with their latest commits
    branches = db.query(Branch).filter(Branch.repo_id == repo_id).order_by(
        desc(Branch.is_default), desc(Branch.updated_at)
    ).all()
    
    # Get recent events that represent commits (push events)
    commit_events = db.query(Event).filter(
        and_(
            Event.repo_id == repo_id,
            Event.event_type == "push"
        )
    ).order_by(desc(Event.created_at)).limit(limit).all()
    
    # Get pull requests for merge information
    pull_requests = db.query(PullRequest).filter(
        PullRequest.repo_id == repo_id
    ).order_by(desc(PullRequest.updated_at)).limit(50).all()
    
    # Build graph data structure
    graph_data = {
        "repository": {
            "id": repo.id,
            "full_name": repo.full_name,
            "default_branch": repo.default_branch
        },
        "branches": [
            {
                "name": branch.name,
                "head_sha": branch.head_sha,
                "is_default": branch.is_default,
                "is_protected": branch.is_protected,
                "last_commit": {
                    "sha": branch.head_sha,
                    "message": branch.last_commit_message,
                    "author": branch.last_commit_author,
                    "date": branch.last_commit_date.isoformat() if branch.last_commit_date else None
                },
                "updated_at": branch.updated_at.isoformat() if branch.updated_at else None
            }
            for branch in branches
        ],
        "commits": [],
        "merges": []
    }
    
    # Process commit events to build commit history
    for event in commit_events:
        try:
            payload = json.loads(event.payload_json)
            commits = payload.get("commits", [])
            ref = payload.get("ref", "").replace("refs/heads/", "")
            
            for commit in commits:
                graph_data["commits"].append({
                    "sha": commit.get("id", "")[:8],
                    "full_sha": commit.get("id", ""),
                    "message": commit.get("message", ""),
                    "author": commit.get("author", {}).get("name", ""),
                    "email": commit.get("author", {}).get("email", ""),
                    "date": commit.get("timestamp", ""),
                    "branch": ref,
                    "event_id": event.id
                })
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse commit event {event.id}: {e}")
    
    # Process pull requests for merge information
    for pr in pull_requests:
        if pr.state == "closed" and pr.merged_at:
            graph_data["merges"].append({
                "pr_number": pr.number,
                "title": pr.title,
                "from_branch": pr.head_ref,
                "to_branch": pr.base_ref,
                "merge_sha": pr.merge_commit_sha,
                "author": pr.author,
                "merged_at": pr.merged_at.isoformat() if pr.merged_at else None
            })
    
    # Sort commits by date (newest first)
    graph_data["commits"].sort(key=lambda x: x["date"], reverse=True)
    
    return graph_data

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

# Template parsing endpoints
@app.post("/api/templates/parse-issue")
async def parse_issue_template(request: Dict[str, Any]):
    """Parse issue body for template data"""
    try:
        body = request.get("body", "")
        labels = request.get("labels", [])
        
        template_data = template_parser.parse_issue_body(body, labels)
        
        return {
            "template_type": template_data.template_type.value,
            "priority": template_data.priority.value,
            "estimated_time": template_data.estimated_time,
            "acceptance_criteria": template_data.acceptance_criteria,
            "technical_requirements": template_data.technical_requirements,
            "branch_suggestion": template_data.branch_suggestion,
            "user_story": template_data.user_story,
            "reproduction_steps": template_data.reproduction_steps,
            "expected_behavior": template_data.expected_behavior,
            "actual_behavior": template_data.actual_behavior,
            "environment_details": template_data.environment_details,
            "task_checklist": template_data.task_checklist,
            "dependencies": template_data.dependencies
        }
    except Exception as e:
        logger.error(f"Template parsing error: {e}")
        raise HTTPException(status_code=500, detail=f"Template parsing failed: {str(e)}")

@app.post("/api/templates/parse-pr")
async def parse_pr_template(request: Dict[str, Any]):
    """Parse PR body for template data"""
    try:
        body = request.get("body", "")
        title = request.get("title", "")
        
        template_data = template_parser.parse_pr_body(body, title)
        
        return {
            "changes_summary": template_data.changes_summary,
            "related_issues": template_data.related_issues,
            "testing_checklist": template_data.testing_checklist,
            "breaking_changes": template_data.breaking_changes,
            "deployment_notes": template_data.deployment_notes
        }
    except Exception as e:
        logger.error(f"PR template parsing error: {e}")
        raise HTTPException(status_code=500, detail=f"PR template parsing failed: {str(e)}")

# Branch naming endpoints
@app.post("/api/branches/validate-name")
async def validate_branch_name(request: Dict[str, Any]):
    """Validate branch name against naming conventions"""
    try:
        branch_name = request.get("branch_name", "")
        branch_type = request.get("branch_type")
        
        if branch_type:
            from src.core.branch_naming import BranchType
            branch_type = BranchType(branch_type)
        
        is_valid, errors = branch_naming_service.validate_branch_name(branch_name, branch_type)
        
        return {
            "is_valid": is_valid,
            "errors": errors,
            "parsed_info": {
                "branch_type": branch_naming_service.parse_branch_name(branch_name).branch_type.value,
                "issue_number": branch_naming_service.parse_branch_name(branch_name).issue_number,
                "description": branch_naming_service.parse_branch_name(branch_name).description
            }
        }
    except Exception as e:
        logger.error(f"Branch validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Branch validation failed: {str(e)}")

@app.post("/api/branches/suggest-name")
async def suggest_branch_name(request: Dict[str, Any]):
    """Suggest branch name based on issue information"""
    try:
        issue_number = request.get("issue_number")
        issue_title = request.get("issue_title", "")
        branch_type = request.get("branch_type", "feature")
        
        from src.core.branch_naming import BranchType
        branch_type_enum = BranchType(branch_type)
        
        suggested_name = branch_naming_service.suggest_branch_name(
            issue_number, issue_title, branch_type_enum
        )
        
        return {
            "suggested_name": suggested_name,
            "branch_type": branch_type_enum.value,
            "issue_number": issue_number
        }
    except Exception as e:
        logger.error(f"Branch suggestion error: {e}")
        raise HTTPException(status_code=500, detail=f"Branch suggestion failed: {str(e)}")

@app.get("/api/repos/{repo_id}/branch-stats")
async def get_branch_naming_stats(repo_id: int, db: Session = Depends(get_db)):
    """Get branch naming convention statistics"""
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        stats = branch_naming_service.get_naming_convention_stats(db, repo_id)
        
        return stats
    except Exception as e:
        logger.error(f"Branch stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Branch stats failed: {str(e)}")

@app.get("/api/repos/{repo_id}/issues/{issue_number}/related-branches")
async def get_issue_related_branches(repo_id: int, issue_number: int, db: Session = Depends(get_db)):
    """Get branches related to a specific issue"""
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        related_branches = branch_naming_service.find_related_branches(db, issue_number, repo_id)
        
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
                "updated_at": branch.updated_at.isoformat() if branch.updated_at else None
            }
            for branch in related_branches
        ]
    except Exception as e:
        logger.error(f"Related branches error: {e}")
        raise HTTPException(status_code=500, detail=f"Related branches failed: {str(e)}")

# Time-boxed development endpoints
@app.post("/api/repos/{repo_id}/timeboxes")
async def create_time_box(
    repo_id: int,
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Create a new hackathon time box"""
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        name = request.get("name")
        phase = request.get("phase")
        duration_hours = request.get("duration_hours", 4)
        description = request.get("description", "")
        start_time_str = request.get("start_time")
        
        if not name or not phase:
            raise HTTPException(status_code=400, detail="Name and phase are required")
        
        # Parse start time or use current time
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
        else:
            start_time = datetime.utcnow()
        
        time_box = timebox_service.create_time_box(
            db, repo_id, name, phase, start_time, duration_hours, description
        )
        
        return {
            "id": time_box.id,
            "name": time_box.name,
            "phase": time_box.phase,
            "start_time": time_box.start_time.isoformat(),
            "end_time": time_box.end_time.isoformat(),
            "description": time_box.description,
            "is_active": time_box.is_active,
            "remaining_hours": timebox_service._calculate_remaining_hours(time_box)
        }
    except Exception as e:
        logger.error(f"Create time box error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create time box: {str(e)}")

@app.get("/api/repos/{repo_id}/timeboxes")
async def get_time_boxes(repo_id: int, db: Session = Depends(get_db)):
    """Get all time boxes for a repository"""
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        time_boxes = timebox_service.get_time_boxes(db, repo_id)
        
        return [
            {
                "id": tb.id,
                "name": tb.name,
                "phase": tb.phase,
                "start_time": tb.start_time.isoformat(),
                "end_time": tb.end_time.isoformat(),
                "description": tb.description,
                "is_active": tb.is_active,
                "remaining_hours": timebox_service._calculate_remaining_hours(tb),
                "created_at": tb.created_at.isoformat()
            }
            for tb in time_boxes
        ]
    except Exception as e:
        logger.error(f"Get time boxes error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get time boxes: {str(e)}")

@app.get("/api/repos/{repo_id}/timeboxes/active")
async def get_active_time_box(repo_id: int, db: Session = Depends(get_db)):
    """Get the currently active time box"""
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        time_box = timebox_service.get_active_time_box(db, repo_id)
        
        if not time_box:
            return None
        
        return {
            "id": time_box.id,
            "name": time_box.name,
            "phase": time_box.phase,
            "start_time": time_box.start_time.isoformat(),
            "end_time": time_box.end_time.isoformat(),
            "description": time_box.description,
            "is_active": time_box.is_active,
            "remaining_hours": timebox_service._calculate_remaining_hours(time_box)
        }
    except Exception as e:
        logger.error(f"Get active time box error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get active time box: {str(e)}")

@app.post("/api/repos/{repo_id}/issues/{issue_id}/deadline")
async def set_issue_deadline(
    repo_id: int,
    issue_id: int,
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Set deadline and time tracking for an issue"""
    try:
        deadline_str = request.get("deadline")
        estimated_hours = request.get("estimated_hours")
        
        if not deadline_str:
            raise HTTPException(status_code=400, detail="Deadline is required")
        
        deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
        
        issue = timebox_service.set_issue_deadline(db, issue_id, deadline, estimated_hours)
        
        return {
            "id": issue.id,
            "deadline": issue.deadline.isoformat() if issue.deadline else None,
            "estimated_hours": issue.estimated_hours,
            "time_box_start": issue.time_box_start.isoformat() if issue.time_box_start else None,
            "time_box_end": issue.time_box_end.isoformat() if issue.time_box_end else None
        }
    except Exception as e:
        logger.error(f"Set issue deadline error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to set deadline: {str(e)}")

@app.post("/api/repos/{repo_id}/issues/{issue_id}/start-work")
async def start_issue_work(repo_id: int, issue_id: int, db: Session = Depends(get_db)):
    """Start time tracking for an issue"""
    try:
        issue = timebox_service.start_issue_work(db, issue_id)
        
        return {
            "id": issue.id,
            "time_box_start": issue.time_box_start.isoformat() if issue.time_box_start else None,
            "time_box_end": issue.time_box_end.isoformat() if issue.time_box_end else None,
            "estimated_hours": issue.estimated_hours
        }
    except Exception as e:
        logger.error(f"Start issue work error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start work: {str(e)}")

@app.get("/api/repos/{repo_id}/issues/time-sensitive")
async def get_time_sensitive_issues(
    repo_id: int,
    hours_threshold: int = Query(24, description="Hours threshold for time sensitivity"),
    db: Session = Depends(get_db)
):
    """Get issues approaching their deadlines"""
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        issues = timebox_service.get_time_sensitive_issues(db, repo_id, hours_threshold)
        
        return [
            {
                "id": issue.id,
                "number": issue.number,
                "title": issue.title,
                "deadline": issue.deadline.isoformat() if issue.deadline else None,
                "estimated_hours": issue.estimated_hours,
                "priority_escalated": issue.priority_escalated,
                "hours_until_deadline": (issue.deadline - datetime.utcnow()).total_seconds() / 3600 if issue.deadline else None
            }
            for issue in issues
        ]
    except Exception as e:
        logger.error(f"Get time sensitive issues error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get time sensitive issues: {str(e)}")

@app.post("/api/repos/{repo_id}/issues/escalate-overdue")
async def escalate_overdue_issues(repo_id: int, db: Session = Depends(get_db)):
    """Automatically escalate overdue issues"""
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        escalated_issues = timebox_service.escalate_overdue_issues(db, repo_id)
        
        return {
            "escalated_count": len(escalated_issues),
            "escalated_issues": [
                {
                    "id": issue.id,
                    "number": issue.number,
                    "title": issue.title,
                    "deadline": issue.deadline.isoformat() if issue.deadline else None
                }
                for issue in escalated_issues
            ]
        }
    except Exception as e:
        logger.error(f"Escalate overdue issues error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to escalate issues: {str(e)}")

@app.get("/api/repos/{repo_id}/timebox-stats")
async def get_time_box_statistics(repo_id: int, db: Session = Depends(get_db)):
    """Get time-boxed development statistics"""
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        stats = timebox_service.get_time_box_statistics(db, repo_id)
        return stats
    except Exception as e:
        logger.error(f"Get time box stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.get("/api/repos/{repo_id}/phase-recommendations")
async def get_phase_recommendations(repo_id: int, db: Session = Depends(get_db)):
    """Get hackathon phase transition recommendations"""
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        recommendations = timebox_service.get_phase_recommendations(db, repo_id)
        return recommendations
    except Exception as e:
        logger.error(f"Get phase recommendations error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@app.post("/api/repos/{repo_id}/rapid-issue")
async def create_rapid_issue(
    repo_id: int,
    request: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Create a rapid issue for hackathon development"""
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        title = request.get("title")
        issue_type = request.get("type", "task")
        priority = request.get("priority", "medium")
        estimated_hours = request.get("estimated_hours", 2)
        
        if not title:
            raise HTTPException(status_code=400, detail="Title is required")
        
        rapid_issue = timebox_service.create_rapid_issue(
            db, repo_id, title, issue_type, priority, estimated_hours
        )
        
        return rapid_issue
    except Exception as e:
        logger.error(f"Create rapid issue error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create rapid issue: {str(e)}")

@app.get("/api/repos/{repo_id}/hackathon-dashboard")
async def get_hackathon_dashboard_data(repo_id: int, db: Session = Depends(get_db)):
    """Get optimized dashboard data for hackathon development"""
    try:
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Get all open issues with template data
        issues = db.query(Issue).filter(
            and_(Issue.repo_id == repo_id, Issue.state == "open")
        ).all()
        
        dashboard_issues = []
        for issue in issues:
            labels = json.loads(issue.labels_json) if issue.labels_json else []
            assignees = json.loads(issue.assignees_json) if issue.assignees_json else []
            
            # Parse template data
            template_data = template_parser.parse_issue_body(issue.body, labels)
            
            # Prepare timebox data
            timebox_data = {
                'hackathon_phase': issue.hackathon_phase,
                'hours_until_deadline': (issue.deadline - datetime.utcnow()).total_seconds() / 3600 if issue.deadline else None,
                'is_overdue': issue.deadline < datetime.utcnow() if issue.deadline else False,
                'priority_escalated': issue.priority_escalated,
                'time_remaining_percentage': _calculate_time_remaining_percentage(issue) if issue.time_box_start and issue.time_box_end else None
            }
            
            # Map to dashboard data
            dashboard_data = status_mapping_service.map_issue_to_dashboard(
                template_data,
                labels=labels,
                assignees=assignees,
                issue_state=issue.state,
                timebox_data=timebox_data
            )
            
            dashboard_issues.append(dashboard_data)
        
        # Get optimized dashboard data
        optimized_data = status_mapping_service.optimize_for_hackathon_dashboard(dashboard_issues)
        
        # Add repository context
        optimized_data['repository'] = {
            'id': repo.id,
            'name': repo.name,
            'full_name': repo.full_name
        }
        
        # Add time box context
        active_time_box = timebox_service.get_active_time_box(db, repo_id)
        if active_time_box:
            optimized_data['active_time_box'] = {
                'name': active_time_box.name,
                'phase': active_time_box.phase,
                'remaining_hours': timebox_service._calculate_remaining_hours(active_time_box)
            }
        
        return optimized_data
    except Exception as e:
        logger.error(f"Get hackathon dashboard error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # ログ設定
    logger.info("Starting Hack PM Backend Server...")
    logger.info("API will be available at:")
    logger.info("  - http://localhost:8000")
    logger.info("  - http://127.0.0.1:8000")
    logger.info("  - http://0.0.0.0:8000")
    logger.info("API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True
    )