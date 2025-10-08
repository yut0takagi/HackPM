"""
GitHub Webhook handler and API integration
"""
import os
import hmac
import hashlib
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import HTTPException, Request, Depends
from sqlalchemy.orm import Session
from ..services.database import get_db, Repository, Branch, PullRequest, Issue, CIRun, Event
import httpx

logger = logging.getLogger(__name__)

class GitHubWebhookHandler:
    def __init__(self):
        self.webhook_secret = os.getenv("GITHUB_WEBHOOK_SECRET", "")
        self.github_token = os.getenv("GITHUB_TOKEN", "")
        self.allowed_repos = self._parse_allowed_repos()
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
        
    def _parse_allowed_repos(self) -> List[str]:
        """Parse ALLOWED_REPOS environment variable"""
        allowed = os.getenv("ALLOWED_REPOS", "")
        if not allowed:
            return []
        return [repo.strip() for repo in allowed.split(",") if repo.strip()]
    
    def verify_signature(self, payload_body: bytes, signature_header: str) -> bool:
        """Verify GitHub webhook signature"""
        if not self.webhook_secret:
            logger.warning("GITHUB_WEBHOOK_SECRET not set, skipping signature verification")
            return True
            
        if not signature_header:
            return False
            
        try:
            hash_object = hmac.new(
                self.webhook_secret.encode('utf-8'),
                msg=payload_body,
                digestmod=hashlib.sha256
            )
            expected_signature = "sha256=" + hash_object.hexdigest()
            return hmac.compare_digest(expected_signature, signature_header)
        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
    
    def is_repo_allowed(self, repo_full_name: str) -> bool:
        """Check if repository is in allowed list"""
        if not self.allowed_repos:
            return True  # If no allowlist, allow all
        return repo_full_name in self.allowed_repos
    
    async def handle_webhook(
        self, 
        request: Request, 
        db: Session = Depends(get_db)
    ) -> Dict[str, Any]:
        """Main webhook handler"""
        try:
            # Get headers
            event_type = request.headers.get("X-GitHub-Event")
            delivery_id = request.headers.get("X-GitHub-Delivery")
            signature = request.headers.get("X-Hub-Signature-256")
            
            if not event_type:
                raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header")
            
            # Get payload
            payload_body = await request.body()
            
            # Verify signature
            if not self.verify_signature(payload_body, signature):
                raise HTTPException(status_code=401, detail="Invalid signature")
            
            # Parse payload
            try:
                payload = json.loads(payload_body.decode('utf-8'))
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON payload")
            
            # Check repository allowlist
            repo_data = payload.get("repository", {})
            repo_full_name = repo_data.get("full_name", "")
            
            if not self.is_repo_allowed(repo_full_name):
                logger.info(f"Repository {repo_full_name} not in allowlist, ignoring")
                return {"message": "Repository not allowed", "status": "ignored"}
            
            # Ensure repository exists in DB
            repo = await self.ensure_repository(db, repo_data)
            
            # Store event
            event = Event(
                repo_id=repo.id,
                event_type=event_type,
                action=payload.get("action"),
                payload_json=json.dumps(payload),
                delivery_id=delivery_id,
                actor=payload.get("sender", {}).get("login"),
                created_at=datetime.utcnow()
            )
            db.add(event)
            
            # Process specific event types
            result = await self.process_event(db, event_type, payload, repo)
            
            # Send Discord notification for important events
            await self.send_discord_notification(event_type, payload, repo_full_name)
            
            db.commit()
            
            return {
                "message": "Webhook processed successfully",
                "event_type": event_type,
                "repository": repo_full_name,
                "result": result
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    async def ensure_repository(self, db: Session, repo_data: Dict[str, Any]) -> Repository:
        """Ensure repository exists in database"""
        full_name = repo_data.get("full_name")
        if not full_name:
            raise ValueError("Repository full_name is required")
        
        repo = db.query(Repository).filter(Repository.full_name == full_name).first()
        
        if not repo:
            repo = Repository(
                full_name=full_name,
                name=repo_data.get("name", ""),
                owner=repo_data.get("owner", {}).get("login", ""),
                default_branch=repo_data.get("default_branch", "main"),
                visibility=repo_data.get("visibility", "private"),
                description=repo_data.get("description"),
                html_url=repo_data.get("html_url"),
                clone_url=repo_data.get("clone_url"),
                ssh_url=repo_data.get("ssh_url"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(repo)
            db.flush()  # Get the ID
        else:
            # Update repository info
            repo.name = repo_data.get("name", repo.name)
            repo.default_branch = repo_data.get("default_branch", repo.default_branch)
            repo.visibility = repo_data.get("visibility", repo.visibility)
            repo.description = repo_data.get("description", repo.description)
            repo.html_url = repo_data.get("html_url", repo.html_url)
            repo.updated_at = datetime.utcnow()
        
        return repo
    
    async def process_event(
        self, 
        db: Session, 
        event_type: str, 
        payload: Dict[str, Any], 
        repo: Repository
    ) -> Dict[str, Any]:
        """Process specific event types"""
        
        if event_type == "push":
            return await self.process_push_event(db, payload, repo)
        elif event_type == "pull_request":
            return await self.process_pull_request_event(db, payload, repo)
        elif event_type == "issues":
            return await self.process_issues_event(db, payload, repo)
        elif event_type == "create" or event_type == "delete":
            return await self.process_branch_event(db, payload, repo, event_type)
        elif event_type == "workflow_run":
            return await self.process_workflow_run_event(db, payload, repo)
        else:
            logger.info(f"Unhandled event type: {event_type}")
            return {"message": f"Event type {event_type} logged but not processed"}
    
    async def process_push_event(
        self, 
        db: Session, 
        payload: Dict[str, Any], 
        repo: Repository
    ) -> Dict[str, Any]:
        """Process push events"""
        ref = payload.get("ref", "")
        if not ref.startswith("refs/heads/"):
            return {"message": "Not a branch push, ignoring"}
        
        branch_name = ref.replace("refs/heads/", "")
        head_commit = payload.get("head_commit", {})
        
        # Update or create branch
        branch = db.query(Branch).filter(
            Branch.repo_id == repo.id,
            Branch.name == branch_name
        ).first()
        
        if not branch:
            branch = Branch(
                repo_id=repo.id,
                name=branch_name,
                head_sha=payload.get("after", ""),
                is_default=(branch_name == repo.default_branch),
                last_commit_message=head_commit.get("message"),
                last_commit_author=head_commit.get("author", {}).get("name"),
                last_commit_date=self._parse_datetime(head_commit.get("timestamp")),
                pushed_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(branch)
        else:
            branch.head_sha = payload.get("after", branch.head_sha)
            branch.last_commit_message = head_commit.get("message", branch.last_commit_message)
            branch.last_commit_author = head_commit.get("author", {}).get("name", branch.last_commit_author)
            branch.last_commit_date = self._parse_datetime(head_commit.get("timestamp")) or branch.last_commit_date
            branch.pushed_at = datetime.utcnow()
            branch.updated_at = datetime.utcnow()
        
        return {"message": f"Branch {branch_name} updated", "commits": len(payload.get("commits", []))}
    
    async def process_pull_request_event(
        self, 
        db: Session, 
        payload: Dict[str, Any], 
        repo: Repository
    ) -> Dict[str, Any]:
        """Process pull request events"""
        action = payload.get("action")
        pr_data = payload.get("pull_request", {})
        
        pr = db.query(PullRequest).filter(
            PullRequest.repo_id == repo.id,
            PullRequest.number == pr_data.get("number")
        ).first()
        
        if not pr:
            pr = PullRequest(
                repo_id=repo.id,
                number=pr_data.get("number"),
                title=pr_data.get("title", ""),
                body=pr_data.get("body", ""),
                author=pr_data.get("user", {}).get("login", ""),
                author_avatar=pr_data.get("user", {}).get("avatar_url", ""),
                state=pr_data.get("state", "open"),
                draft=pr_data.get("draft", False),
                head_ref=pr_data.get("head", {}).get("ref", ""),
                base_ref=pr_data.get("base", {}).get("ref", ""),
                head_sha=pr_data.get("head", {}).get("sha", ""),
                html_url=pr_data.get("html_url", ""),
                mergeable=pr_data.get("mergeable"),
                created_at=self._parse_datetime(pr_data.get("created_at")) or datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(pr)
        else:
            pr.title = pr_data.get("title", pr.title)
            pr.body = pr_data.get("body", pr.body)
            pr.state = pr_data.get("state", pr.state)
            pr.draft = pr_data.get("draft", pr.draft)
            pr.head_sha = pr_data.get("head", {}).get("sha", pr.head_sha)
            pr.mergeable = pr_data.get("mergeable", pr.mergeable)
            pr.updated_at = datetime.utcnow()
            
            if action == "closed" and pr_data.get("merged"):
                pr.merged_at = self._parse_datetime(pr_data.get("merged_at"))
                pr.merge_commit_sha = pr_data.get("merge_commit_sha")
            elif action == "closed":
                pr.closed_at = self._parse_datetime(pr_data.get("closed_at"))
        
        return {"message": f"Pull request #{pr.number} {action}", "state": pr.state}
    
    async def process_issues_event(
        self, 
        db: Session, 
        payload: Dict[str, Any], 
        repo: Repository
    ) -> Dict[str, Any]:
        """Process issues events"""
        action = payload.get("action")
        issue_data = payload.get("issue", {})
        
        issue = db.query(Issue).filter(
            Issue.repo_id == repo.id,
            Issue.number == issue_data.get("number")
        ).first()
        
        if not issue:
            issue = Issue(
                repo_id=repo.id,
                number=issue_data.get("number"),
                title=issue_data.get("title", ""),
                body=issue_data.get("body", ""),
                author=issue_data.get("user", {}).get("login", ""),
                author_avatar=issue_data.get("user", {}).get("avatar_url", ""),
                state=issue_data.get("state", "open"),
                labels_json=json.dumps([label.get("name") for label in issue_data.get("labels", [])]),
                assignees_json=json.dumps([assignee.get("login") for assignee in issue_data.get("assignees", [])]),
                milestone=issue_data.get("milestone", {}).get("title") if issue_data.get("milestone") else None,
                html_url=issue_data.get("html_url", ""),
                created_at=self._parse_datetime(issue_data.get("created_at")) or datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(issue)
        else:
            issue.title = issue_data.get("title", issue.title)
            issue.body = issue_data.get("body", issue.body)
            issue.state = issue_data.get("state", issue.state)
            issue.labels_json = json.dumps([label.get("name") for label in issue_data.get("labels", [])])
            issue.assignees_json = json.dumps([assignee.get("login") for assignee in issue_data.get("assignees", [])])
            issue.milestone = issue_data.get("milestone", {}).get("title") if issue_data.get("milestone") else issue.milestone
            issue.updated_at = datetime.utcnow()
            
            if action == "closed":
                issue.closed_at = self._parse_datetime(issue_data.get("closed_at"))
        
        return {"message": f"Issue #{issue.number} {action}", "state": issue.state}
    
    async def process_branch_event(
        self, 
        db: Session, 
        payload: Dict[str, Any], 
        repo: Repository,
        event_type: str
    ) -> Dict[str, Any]:
        """Process branch create/delete events"""
        ref_type = payload.get("ref_type")
        if ref_type != "branch":
            return {"message": f"Not a branch {event_type}, ignoring"}
        
        branch_name = payload.get("ref")
        
        if event_type == "create":
            # Create new branch
            existing = db.query(Branch).filter(
                Branch.repo_id == repo.id,
                Branch.name == branch_name
            ).first()
            
            if not existing:
                branch = Branch(
                    repo_id=repo.id,
                    name=branch_name,
                    head_sha=payload.get("master_branch", ""),
                    is_default=(branch_name == repo.default_branch),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(branch)
            
            return {"message": f"Branch {branch_name} created"}
        
        elif event_type == "delete":
            # Delete branch
            branch = db.query(Branch).filter(
                Branch.repo_id == repo.id,
                Branch.name == branch_name
            ).first()
            
            if branch:
                db.delete(branch)
            
            return {"message": f"Branch {branch_name} deleted"}
    
    async def process_workflow_run_event(
        self, 
        db: Session, 
        payload: Dict[str, Any], 
        repo: Repository
    ) -> Dict[str, Any]:
        """Process workflow run events"""
        workflow_run = payload.get("workflow_run", {})
        
        ci_run = db.query(CIRun).filter(
            CIRun.repo_id == repo.id,
            CIRun.run_id == str(workflow_run.get("id"))
        ).first()
        
        if not ci_run:
            ci_run = CIRun(
                repo_id=repo.id,
                run_id=str(workflow_run.get("id")),
                workflow_name=workflow_run.get("name", ""),
                workflow_id=str(workflow_run.get("workflow_id", "")),
                status=workflow_run.get("status", ""),
                conclusion=workflow_run.get("conclusion"),
                head_branch=workflow_run.get("head_branch", ""),
                head_sha=workflow_run.get("head_sha", ""),
                event=workflow_run.get("event", ""),
                actor=workflow_run.get("actor", {}).get("login", ""),
                html_url=workflow_run.get("html_url", ""),
                jobs_url=workflow_run.get("jobs_url", ""),
                logs_url=workflow_run.get("logs_url", ""),
                run_started_at=self._parse_datetime(workflow_run.get("run_started_at")),
                run_updated_at=self._parse_datetime(workflow_run.get("updated_at")),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(ci_run)
        else:
            ci_run.status = workflow_run.get("status", ci_run.status)
            ci_run.conclusion = workflow_run.get("conclusion", ci_run.conclusion)
            ci_run.run_updated_at = self._parse_datetime(workflow_run.get("updated_at")) or ci_run.run_updated_at
            ci_run.updated_at = datetime.utcnow()
        
        return {
            "message": f"Workflow run {ci_run.run_id} updated", 
            "status": ci_run.status,
            "conclusion": ci_run.conclusion
        }
    
    async def send_discord_notification(
        self, 
        event_type: str, 
        payload: Dict[str, Any], 
        repo_name: str
    ):
        """Send Discord notification for important events"""
        if not self.discord_webhook_url:
            return
        
        message = None
        
        if event_type == "push":
            ref = payload.get("ref", "")
            if ref == f"refs/heads/{payload.get('repository', {}).get('default_branch', 'main')}":
                commits = payload.get("commits", [])
                if payload.get("forced"):
                    message = f"🚨 **Force push** to {repo_name} main branch! {len(commits)} commits"
                elif len(commits) > 10:
                    message = f"📦 Large push to {repo_name}: {len(commits)} commits"
        
        elif event_type == "pull_request":
            action = payload.get("action")
            pr = payload.get("pull_request", {})
            if action == "opened":
                message = f"🔄 New PR opened in {repo_name}: #{pr.get('number')} - {pr.get('title')}"
            elif action == "closed" and pr.get("merged"):
                message = f"✅ PR merged in {repo_name}: #{pr.get('number')} - {pr.get('title')}"
        
        elif event_type == "workflow_run":
            workflow_run = payload.get("workflow_run", {})
            if workflow_run.get("conclusion") == "failure":
                message = f"❌ CI failed in {repo_name}: {workflow_run.get('name')} on {workflow_run.get('head_branch')}"
            elif workflow_run.get("conclusion") == "success" and workflow_run.get("head_branch") == payload.get("repository", {}).get("default_branch"):
                message = f"✅ CI passed on {repo_name} main branch: {workflow_run.get('name')}"
        
        if message:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(
                        self.discord_webhook_url,
                        json={"content": message},
                        timeout=10.0
                    )
            except Exception as e:
                logger.error(f"Failed to send Discord notification: {e}")
    
    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """Parse GitHub datetime string"""
        if not dt_string:
            return None
        try:
            # GitHub uses ISO format: 2023-01-01T12:00:00Z
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00')).replace(tzinfo=None)
        except (ValueError, AttributeError):
            return None

# Global instance
webhook_handler = GitHubWebhookHandler()