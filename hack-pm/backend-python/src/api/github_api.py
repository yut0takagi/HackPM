"""
GitHub API integration for data synchronization
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..services.database import get_db, Repository, Branch, PullRequest, Issue, CIRun
from ..core.template_parser import template_parser
from ..core.status_mapping import status_mapping_service
from ..core.branch_naming import branch_naming_service
import httpx

logger = logging.getLogger(__name__)

class GitHubAPIClient:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN", "")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "hack-pm/1.0"
        }
        self.allowed_repos = self._parse_allowed_repos()
    
    def _parse_allowed_repos(self) -> List[str]:
        """Parse ALLOWED_REPOS environment variable"""
        allowed = os.getenv("ALLOWED_REPOS", "")
        if not allowed:
            return []
        return [repo.strip() for repo in allowed.split(",") if repo.strip()]
    
    async def sync_repositories(self, db: Session):
        """Sync repository information for all allowed repos"""
        if not self.token:
            logger.warning("GITHUB_TOKEN not set, skipping repository sync")
            return
        
        for repo_full_name in self.allowed_repos:
            try:
                await self.sync_single_repository(db, repo_full_name)
            except Exception as e:
                logger.error(f"Failed to sync repository {repo_full_name}: {e}")
        
        db.commit()
    
    async def sync_single_repository(self, db: Session, repo_full_name: str):
        """Sync a single repository"""
        async with httpx.AsyncClient() as client:
            # Get repository info
            repo_url = f"{self.base_url}/repos/{repo_full_name}"
            response = await client.get(repo_url, headers=self.headers)
            
            if response.status_code == 404:
                logger.warning(f"Repository {repo_full_name} not found or not accessible")
                return
            elif response.status_code != 200:
                logger.error(f"Failed to fetch repository {repo_full_name}: {response.status_code}")
                return
            
            repo_data = response.json()
            
            # Update or create repository
            repo = db.query(Repository).filter(Repository.full_name == repo_full_name).first()
            
            if not repo:
                repo = Repository(
                    full_name=repo_full_name,
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
                db.flush()
            else:
                repo.name = repo_data.get("name", repo.name)
                repo.default_branch = repo_data.get("default_branch", repo.default_branch)
                repo.visibility = repo_data.get("visibility", repo.visibility)
                repo.description = repo_data.get("description", repo.description)
                repo.html_url = repo_data.get("html_url", repo.html_url)
                repo.updated_at = datetime.utcnow()
            
            # Sync branches, PRs, issues, and CI runs
            await self.sync_branches(client, db, repo, repo_full_name)
            await self.sync_pull_requests(client, db, repo, repo_full_name)
            await self.sync_issues(client, db, repo, repo_full_name)
            await self.sync_workflow_runs(client, db, repo, repo_full_name)
            
            # Link branches to issues based on naming conventions
            try:
                branch_links = branch_naming_service.link_branches_to_issues(db, repo.id)
                logger.info(f"Created {len(branch_links)} branch-issue links for {repo_full_name}")
            except Exception as e:
                logger.error(f"Failed to link branches to issues for {repo_full_name}: {e}")
    
    async def sync_branches(self, client: httpx.AsyncClient, db: Session, repo: Repository, repo_full_name: str):
        """Sync repository branches"""
        try:
            branches_url = f"{self.base_url}/repos/{repo_full_name}/branches"
            response = await client.get(branches_url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch branches for {repo_full_name}: {response.status_code}")
                return
            
            branches_data = response.json()
            
            for branch_data in branches_data:
                branch_name = branch_data.get("name")
                commit_data = branch_data.get("commit", {})
                
                branch = db.query(Branch).filter(
                    Branch.repo_id == repo.id,
                    Branch.name == branch_name
                ).first()
                
                if not branch:
                    branch = Branch(
                        repo_id=repo.id,
                        name=branch_name,
                        head_sha=commit_data.get("sha", ""),
                        is_default=(branch_name == repo.default_branch),
                        is_protected=branch_data.get("protected", False),
                        last_commit_message=commit_data.get("commit", {}).get("message"),
                        last_commit_author=commit_data.get("commit", {}).get("author", {}).get("name"),
                        last_commit_date=self._parse_datetime(commit_data.get("commit", {}).get("author", {}).get("date")),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(branch)
                else:
                    branch.head_sha = commit_data.get("sha", branch.head_sha)
                    branch.is_protected = branch_data.get("protected", branch.is_protected)
                    branch.last_commit_message = commit_data.get("commit", {}).get("message", branch.last_commit_message)
                    branch.last_commit_author = commit_data.get("commit", {}).get("author", {}).get("name", branch.last_commit_author)
                    branch.last_commit_date = self._parse_datetime(commit_data.get("commit", {}).get("author", {}).get("date")) or branch.last_commit_date
                    branch.updated_at = datetime.utcnow()
        
        except Exception as e:
            logger.error(f"Error syncing branches for {repo_full_name}: {e}")
    
    async def sync_pull_requests(self, client: httpx.AsyncClient, db: Session, repo: Repository, repo_full_name: str):
        """Sync repository pull requests"""
        try:
            # Get open PRs
            prs_url = f"{self.base_url}/repos/{repo_full_name}/pulls"
            params = {"state": "open", "per_page": 100}
            response = await client.get(prs_url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch PRs for {repo_full_name}: {response.status_code}")
                return
            
            prs_data = response.json()
            
            for pr_data in prs_data:
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
        
        except Exception as e:
            logger.error(f"Error syncing PRs for {repo_full_name}: {e}")
    
    async def sync_issues(self, client: httpx.AsyncClient, db: Session, repo: Repository, repo_full_name: str):
        """Sync repository issues"""
        try:
            # Get open issues
            issues_url = f"{self.base_url}/repos/{repo_full_name}/issues"
            params = {"state": "open", "per_page": 100}
            response = await client.get(issues_url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch issues for {repo_full_name}: {response.status_code}")
                return
            
            issues_data = response.json()
            
            for issue_data in issues_data:
                # Skip pull requests (they appear in issues API)
                if issue_data.get("pull_request"):
                    continue
                
                issue = db.query(Issue).filter(
                    Issue.repo_id == repo.id,
                    Issue.number == issue_data.get("number")
                ).first()
                
                # Parse template data from issue body
                labels = [label.get("name") for label in issue_data.get("labels", [])]
                template_data = template_parser.parse_issue_body(issue_data.get("body", ""), labels)
                
                # Map to dashboard data
                dashboard_data = status_mapping_service.map_issue_to_dashboard(
                    template_data,
                    labels=labels,
                    assignees=[assignee.get("login") for assignee in issue_data.get("assignees", [])],
                    issue_state=issue_data.get("state", "open")
                )
                
                # Store template and dashboard data as JSON
                template_json = json.dumps({
                    "template_type": template_data.template_type.value,
                    "priority": template_data.priority.value,
                    "estimated_time": template_data.estimated_time,
                    "acceptance_criteria": template_data.acceptance_criteria,
                    "technical_requirements": template_data.technical_requirements,
                    "branch_suggestion": template_data.branch_suggestion,
                    "user_story": template_data.user_story
                })
                
                dashboard_json = json.dumps({
                    "status": dashboard_data.status.value,
                    "category": dashboard_data.category.value,
                    "priority": dashboard_data.priority.value,
                    "progress_percentage": dashboard_data.progress_percentage,
                    "estimated_hours": dashboard_data.estimated_hours,
                    "acceptance_criteria_total": dashboard_data.acceptance_criteria_total,
                    "acceptance_criteria_completed": dashboard_data.acceptance_criteria_completed
                })

                if not issue:
                    issue = Issue(
                        repo_id=repo.id,
                        number=issue_data.get("number"),
                        title=issue_data.get("title", ""),
                        body=issue_data.get("body", ""),
                        author=issue_data.get("user", {}).get("login", ""),
                        author_avatar=issue_data.get("user", {}).get("avatar_url", ""),
                        state=issue_data.get("state", "open"),
                        labels_json=json.dumps(labels),
                        assignees_json=json.dumps([assignee.get("login") for assignee in issue_data.get("assignees", [])]),
                        milestone=issue_data.get("milestone", {}).get("title") if issue_data.get("milestone") else None,
                        html_url=issue_data.get("html_url", ""),
                        created_at=self._parse_datetime(issue_data.get("created_at")) or datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    # Add template data fields if they don't exist in the model
                    if hasattr(issue, 'template_data_json'):
                        issue.template_data_json = template_json
                    if hasattr(issue, 'dashboard_data_json'):
                        issue.dashboard_data_json = dashboard_json
                    db.add(issue)
                else:
                    issue.title = issue_data.get("title", issue.title)
                    issue.body = issue_data.get("body", issue.body)
                    issue.state = issue_data.get("state", issue.state)
                    issue.labels_json = json.dumps(labels)
                    issue.assignees_json = json.dumps([assignee.get("login") for assignee in issue_data.get("assignees", [])])
                    issue.milestone = issue_data.get("milestone", {}).get("title") if issue_data.get("milestone") else issue.milestone
                    # Update template data fields if they exist in the model
                    if hasattr(issue, 'template_data_json'):
                        issue.template_data_json = template_json
                    if hasattr(issue, 'dashboard_data_json'):
                        issue.dashboard_data_json = dashboard_json
                    issue.updated_at = datetime.utcnow()
        
        except Exception as e:
            logger.error(f"Error syncing issues for {repo_full_name}: {e}")
    
    async def sync_workflow_runs(self, client: httpx.AsyncClient, db: Session, repo: Repository, repo_full_name: str):
        """Sync repository workflow runs"""
        try:
            # Get recent workflow runs
            runs_url = f"{self.base_url}/repos/{repo_full_name}/actions/runs"
            params = {"per_page": 50}
            response = await client.get(runs_url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch workflow runs for {repo_full_name}: {response.status_code}")
                return
            
            runs_data = response.json().get("workflow_runs", [])
            
            for run_data in runs_data:
                ci_run = db.query(CIRun).filter(
                    CIRun.repo_id == repo.id,
                    CIRun.run_id == str(run_data.get("id"))
                ).first()
                
                if not ci_run:
                    ci_run = CIRun(
                        repo_id=repo.id,
                        run_id=str(run_data.get("id")),
                        workflow_name=run_data.get("name", ""),
                        workflow_id=str(run_data.get("workflow_id", "")),
                        status=run_data.get("status", ""),
                        conclusion=run_data.get("conclusion"),
                        head_branch=run_data.get("head_branch", ""),
                        head_sha=run_data.get("head_sha", ""),
                        event=run_data.get("event", ""),
                        actor=run_data.get("actor", {}).get("login", ""),
                        html_url=run_data.get("html_url", ""),
                        jobs_url=run_data.get("jobs_url", ""),
                        logs_url=run_data.get("logs_url", ""),
                        run_started_at=self._parse_datetime(run_data.get("run_started_at")),
                        run_updated_at=self._parse_datetime(run_data.get("updated_at")),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(ci_run)
                else:
                    ci_run.status = run_data.get("status", ci_run.status)
                    ci_run.conclusion = run_data.get("conclusion", ci_run.conclusion)
                    ci_run.run_updated_at = self._parse_datetime(run_data.get("updated_at")) or ci_run.run_updated_at
                    ci_run.updated_at = datetime.utcnow()
        
        except Exception as e:
            logger.error(f"Error syncing workflow runs for {repo_full_name}: {e}")
    
    def _parse_datetime(self, dt_string: Optional[str]) -> Optional[datetime]:
        """Parse GitHub datetime string"""
        if not dt_string:
            return None
        try:
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00')).replace(tzinfo=None)
        except (ValueError, AttributeError):
            return None

# Global instance
github_api = GitHubAPIClient()