"""
Test data insertion script for hack-pm
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, Repository, Branch, PullRequest, Issue, CIRun, Event
from datetime import datetime
import json

def create_test_data():
    db = SessionLocal()
    
    try:
        # Create test repository
        test_repo = Repository(
            full_name="test-org/test-repo",
            name="test-repo",
            owner="test-org",
            default_branch="main",
            visibility="public",
            description="Test repository for hack-pm demonstration",
            html_url="https://github.com/test-org/test-repo",
            clone_url="https://github.com/test-org/test-repo.git",
            ssh_url="git@github.com:test-org/test-repo.git",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(test_repo)
        db.flush()
        
        # Create test branches
        main_branch = Branch(
            repo_id=test_repo.id,
            name="main",
            head_sha="abc123def456",
            is_default=True,
            last_commit_message="Initial commit",
            last_commit_author="Test User",
            last_commit_date=datetime.utcnow(),
            pushed_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(main_branch)
        
        feature_branch = Branch(
            repo_id=test_repo.id,
            name="feature/new-feature",
            head_sha="def456ghi789",
            is_default=False,
            last_commit_message="Add new feature",
            last_commit_author="Developer",
            last_commit_date=datetime.utcnow(),
            pushed_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(feature_branch)
        
        # Create test pull request
        test_pr = PullRequest(
            repo_id=test_repo.id,
            number=1,
            title="Add awesome new feature",
            body="This PR adds an awesome new feature to the application.",
            author="developer",
            author_avatar="https://github.com/images/error/developer_happy.gif",
            state="open",
            draft=False,
            head_ref="feature/new-feature",
            base_ref="main",
            head_sha="def456ghi789",
            html_url="https://github.com/test-org/test-repo/pull/1",
            mergeable=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(test_pr)
        
        # Create test issue
        test_issue = Issue(
            repo_id=test_repo.id,
            number=1,
            title="Bug: Application crashes on startup",
            body="The application crashes when starting up with the following error...",
            author="user123",
            author_avatar="https://github.com/images/error/user123_happy.gif",
            state="open",
            labels_json=json.dumps(["bug", "high-priority"]),
            assignees_json=json.dumps(["developer"]),
            html_url="https://github.com/test-org/test-repo/issues/1",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(test_issue)
        
        # Create test CI run
        test_ci = CIRun(
            repo_id=test_repo.id,
            run_id="123456789",
            workflow_name="CI",
            workflow_id="987654321",
            status="completed",
            conclusion="success",
            head_branch="main",
            head_sha="abc123def456",
            event="push",
            actor="developer",
            html_url="https://github.com/test-org/test-repo/actions/runs/123456789",
            run_started_at=datetime.utcnow(),
            run_updated_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(test_ci)
        
        # Create test events
        push_event = Event(
            repo_id=test_repo.id,
            event_type="push",
            action=None,
            payload_json=json.dumps({
                "ref": "refs/heads/main",
                "commits": [{"message": "Initial commit", "author": {"name": "Test User"}}]
            }),
            delivery_id="event-123",
            actor="testuser",
            ref="refs/heads/main",
            after_sha="abc123def456",
            created_at=datetime.utcnow()
        )
        db.add(push_event)
        
        pr_event = Event(
            repo_id=test_repo.id,
            event_type="pull_request",
            action="opened",
            payload_json=json.dumps({
                "action": "opened",
                "pull_request": {"number": 1, "title": "Add awesome new feature"}
            }),
            delivery_id="event-124",
            actor="developer",
            created_at=datetime.utcnow()
        )
        db.add(pr_event)
        
        db.commit()
        print("✅ Test data created successfully!")
        print(f"📊 Repository: {test_repo.full_name}")
        print(f"🌿 Branches: {main_branch.name}, {feature_branch.name}")
        print(f"🔄 Pull Requests: #{test_pr.number}")
        print(f"🐛 Issues: #{test_issue.number}")
        print(f"⚙️ CI Runs: {test_ci.workflow_name}")
        print(f"📝 Events: {len([push_event, pr_event])}")
        
    except Exception as e:
        print(f"❌ Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()