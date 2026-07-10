"""
Tests for GitHub Webhook handler
"""
import json
import hmac
import hashlib
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
import pytest
from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.services.database import Base, Repository, Branch, PullRequest, Issue, CIRun, Event
from src.api.github_webhook import GitHubWebhookHandler


# Test database setup
@pytest.fixture
def test_db():
    """Create a test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSessionLocal = sessionmaker(bind=engine)
    db = TestSessionLocal()
    yield db
    db.close()


@pytest.fixture
def webhook_handler():
    """Create a webhook handler instance for testing"""
    with patch.dict('os.environ', {
        'GITHUB_WEBHOOK_SECRET': 'test_secret',
        'GITHUB_TOKEN': 'test_token',
        'ALLOWED_REPOS': 'testuser/test-repo',
        'DISCORD_WEBHOOK_URL': 'https://discord.com/api/webhooks/test'
    }):
        handler = GitHubWebhookHandler()
        return handler


@pytest.fixture
def sample_push_payload():
    """Sample push event payload"""
    return {
        "ref": "refs/heads/main",
        "before": "0000000000000000000000000000000000000000",
        "after": "1234567890abcdef1234567890abcdef12345678",
        "repository": {
            "id": 123456789,
            "name": "test-repo",
            "full_name": "testuser/test-repo",
            "owner": {
                "login": "testuser",
                "id": 12345
            },
            "html_url": "https://github.com/testuser/test-repo",
            "default_branch": "main",
            "visibility": "public"
        },
        "pusher": {
            "name": "testuser",
            "email": "test@example.com"
        },
        "sender": {
            "login": "testuser",
            "id": 12345
        },
        "head_commit": {
            "id": "1234567890abcdef1234567890abcdef12345678",
            "message": "Initial commit",
            "timestamp": "2024-01-01T12:00:00Z",
            "author": {
                "name": "Test User",
                "email": "test@example.com"
            }
        },
        "commits": [
            {
                "id": "1234567890abcdef1234567890abcdef12345678",
                "message": "Initial commit",
                "timestamp": "2024-01-01T12:00:00Z",
                "author": {
                    "name": "Test User",
                    "email": "test@example.com"
                }
            }
        ]
    }


@pytest.fixture
def sample_pr_payload():
    """Sample pull request event payload"""
    return {
        "action": "opened",
        "number": 1,
        "pull_request": {
            "id": 987654321,
            "number": 1,
            "title": "Add new feature",
            "body": "This PR adds a new feature to the application.",
            "state": "open",
            "draft": False,
            "user": {
                "login": "testuser",
                "id": 12345,
                "avatar_url": "https://github.com/images/error/testuser_happy.gif"
            },
            "head": {
                "ref": "feature/new-feature",
                "sha": "abcdef1234567890abcdef1234567890abcdef12"
            },
            "base": {
                "ref": "main",
                "sha": "1234567890abcdef1234567890abcdef12345678"
            },
            "html_url": "https://github.com/testuser/test-repo/pull/1",
            "mergeable": True,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z"
        },
        "repository": {
            "id": 123456789,
            "name": "test-repo",
            "full_name": "testuser/test-repo",
            "owner": {
                "login": "testuser",
                "id": 12345
            },
            "html_url": "https://github.com/testuser/test-repo",
            "default_branch": "main",
            "visibility": "public"
        },
        "sender": {
            "login": "testuser",
            "id": 12345
        }
    }


@pytest.fixture
def sample_issue_payload():
    """Sample issue event payload"""
    return {
        "action": "opened",
        "issue": {
            "id": 555666777,
            "number": 1,
            "title": "Bug report",
            "body": "There is a bug in the application.",
            "state": "open",
            "user": {
                "login": "testuser",
                "id": 12345,
                "avatar_url": "https://github.com/images/error/testuser_happy.gif"
            },
            "labels": [
                {
                    "name": "bug",
                    "color": "d73a4a"
                }
            ],
            "assignees": [],
            "milestone": None,
            "html_url": "https://github.com/testuser/test-repo/issues/1",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z"
        },
        "repository": {
            "id": 123456789,
            "name": "test-repo",
            "full_name": "testuser/test-repo",
            "owner": {
                "login": "testuser",
                "id": 12345
            },
            "html_url": "https://github.com/testuser/test-repo",
            "default_branch": "main",
            "visibility": "public"
        },
        "sender": {
            "login": "testuser",
            "id": 12345
        }
    }


class TestWebhookSignatureVerification:
    """Test webhook signature verification"""

    def test_verify_signature_valid(self, webhook_handler):
        """Test signature verification with valid signature"""
        payload = b'{"test": "data"}'
        hash_object = hmac.new(
            b'test_secret',
            msg=payload,
            digestmod=hashlib.sha256
        )
        signature = "sha256=" + hash_object.hexdigest()
        
        assert webhook_handler.verify_signature(payload, signature) is True

    def test_verify_signature_invalid(self, webhook_handler):
        """Test signature verification with invalid signature"""
        payload = b'{"test": "data"}'
        signature = "sha256=invalid_signature"
        
        assert webhook_handler.verify_signature(payload, signature) is False

    def test_verify_signature_missing_secret(self):
        """Test signature verification when secret is not set"""
        with patch.dict('os.environ', {'GITHUB_WEBHOOK_SECRET': ''}):
            handler = GitHubWebhookHandler()
            payload = b'{"test": "data"}'
            signature = "sha256=anything"
            
            # Should return True (skip verification) when secret is not set
            assert handler.verify_signature(payload, signature) is True

    def test_verify_signature_missing_header(self, webhook_handler):
        """Test signature verification with missing signature header"""
        payload = b'{"test": "data"}'
        
        assert webhook_handler.verify_signature(payload, None) is False


class TestRepositoryAllowlist:
    """Test repository allowlist functionality"""

    def test_repo_allowed_in_list(self, webhook_handler):
        """Test repository in allowlist"""
        assert webhook_handler.is_repo_allowed("testuser/test-repo") is True

    def test_repo_not_allowed(self, webhook_handler):
        """Test repository not in allowlist"""
        assert webhook_handler.is_repo_allowed("otheruser/other-repo") is False

    def test_empty_allowlist(self):
        """Test with empty allowlist (should allow all)"""
        with patch.dict('os.environ', {'ALLOWED_REPOS': ''}):
            handler = GitHubWebhookHandler()
            assert handler.is_repo_allowed("anyuser/anyrepo") is True


class TestEnsureRepository:
    """Test repository creation and update"""

    @pytest.mark.asyncio
    async def test_create_new_repository(self, webhook_handler, test_db):
        """Test creating a new repository"""
        repo_data = {
            "full_name": "testuser/test-repo",
            "name": "test-repo",
            "owner": {"login": "testuser"},
            "default_branch": "main",
            "visibility": "public",
            "description": "Test repository",
            "html_url": "https://github.com/testuser/test-repo"
        }
        
        repo = await webhook_handler.ensure_repository(test_db, repo_data)
        
        assert repo is not None
        assert repo.full_name == "testuser/test-repo"
        assert repo.name == "test-repo"
        assert repo.owner == "testuser"
        assert repo.default_branch == "main"

    @pytest.mark.asyncio
    async def test_update_existing_repository(self, webhook_handler, test_db):
        """Test updating an existing repository"""
        # Create initial repository
        repo = Repository(
            full_name="testuser/test-repo",
            name="test-repo",
            owner="testuser",
            default_branch="main",
            visibility="private",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(repo)
        test_db.commit()
        
        # Update with new data
        repo_data = {
            "full_name": "testuser/test-repo",
            "name": "test-repo",
            "owner": {"login": "testuser"},
            "default_branch": "develop",
            "visibility": "public",
            "description": "Updated description"
        }
        
        updated_repo = await webhook_handler.ensure_repository(test_db, repo_data)
        
        assert updated_repo.id == repo.id
        assert updated_repo.default_branch == "develop"
        assert updated_repo.visibility == "public"
        assert updated_repo.description == "Updated description"


class TestProcessPushEvent:
    """Test push event processing"""

    @pytest.mark.asyncio
    async def test_process_push_event_new_branch(self, webhook_handler, test_db, sample_push_payload):
        """Test processing push event for a new branch"""
        # Create repository first
        repo = Repository(
            full_name="testuser/test-repo",
            name="test-repo",
            owner="testuser",
            default_branch="main",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(repo)
        test_db.commit()
        
        result = await webhook_handler.process_push_event(test_db, sample_push_payload, repo)
        
        assert "message" in result
        assert "Branch main updated" in result["message"]
        
        # Verify branch was created
        branch = test_db.query(Branch).filter(
            Branch.repo_id == repo.id,
            Branch.name == "main"
        ).first()
        
        assert branch is not None
        assert branch.head_sha == "1234567890abcdef1234567890abcdef12345678"
        assert branch.last_commit_message == "Initial commit"

    @pytest.mark.asyncio
    async def test_process_push_event_update_branch(self, webhook_handler, test_db, sample_push_payload):
        """Test processing push event for an existing branch"""
        # Create repository and branch
        repo = Repository(
            full_name="testuser/test-repo",
            name="test-repo",
            owner="testuser",
            default_branch="main",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(repo)
        test_db.commit()
        
        branch = Branch(
            repo_id=repo.id,
            name="main",
            head_sha="old_sha",
            is_default=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(branch)
        test_db.commit()
        
        result = await webhook_handler.process_push_event(test_db, sample_push_payload, repo)
        test_db.commit()  # Commit the changes
        
        test_db.refresh(branch)
        assert branch.head_sha == "1234567890abcdef1234567890abcdef12345678"
        assert branch.last_commit_message == "Initial commit"


class TestProcessPullRequestEvent:
    """Test pull request event processing"""

    @pytest.mark.asyncio
    async def test_process_pr_opened(self, webhook_handler, test_db, sample_pr_payload):
        """Test processing opened pull request"""
        repo = Repository(
            full_name="testuser/test-repo",
            name="test-repo",
            owner="testuser",
            default_branch="main",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(repo)
        test_db.commit()
        
        result = await webhook_handler.process_pull_request_event(test_db, sample_pr_payload, repo)
        
        assert "Pull request #1 opened" in result["message"]
        
        pr = test_db.query(PullRequest).filter(
            PullRequest.repo_id == repo.id,
            PullRequest.number == 1
        ).first()
        
        assert pr is not None
        assert pr.title == "Add new feature"
        assert pr.state == "open"
        assert pr.author == "testuser"

    @pytest.mark.asyncio
    async def test_process_pr_update(self, webhook_handler, test_db, sample_pr_payload):
        """Test processing pull request update"""
        repo = Repository(
            full_name="testuser/test-repo",
            name="test-repo",
            owner="testuser",
            default_branch="main",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(repo)
        test_db.commit()
        
        # Create existing PR
        pr = PullRequest(
            repo_id=repo.id,
            number=1,
            title="Old title",
            state="open",
            author="testuser",
            head_ref="feature/new-feature",
            base_ref="main",
            head_sha="old_sha",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(pr)
        test_db.commit()
        
        result = await webhook_handler.process_pull_request_event(test_db, sample_pr_payload, repo)
        test_db.commit()  # Commit the changes
        
        test_db.refresh(pr)
        assert pr.title == "Add new feature"
        assert pr.head_sha == "abcdef1234567890abcdef1234567890abcdef12"


class TestProcessIssuesEvent:
    """Test issues event processing"""

    @pytest.mark.asyncio
    async def test_process_issue_opened(self, webhook_handler, test_db, sample_issue_payload):
        """Test processing opened issue"""
        repo = Repository(
            full_name="testuser/test-repo",
            name="test-repo",
            owner="testuser",
            default_branch="main",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(repo)
        test_db.commit()
        
        result = await webhook_handler.process_issues_event(test_db, sample_issue_payload, repo)
        
        assert "Issue #1 opened" in result["message"]
        
        issue = test_db.query(Issue).filter(
            Issue.repo_id == repo.id,
            Issue.number == 1
        ).first()
        
        assert issue is not None
        assert issue.title == "Bug report"
        assert issue.state == "open"
        assert issue.author == "testuser"
        
        labels = json.loads(issue.labels_json)
        assert "bug" in labels

    @pytest.mark.asyncio
    async def test_process_issue_closed(self, webhook_handler, test_db, sample_issue_payload):
        """Test processing closed issue"""
        repo = Repository(
            full_name="testuser/test-repo",
            name="test-repo",
            owner="testuser",
            default_branch="main",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(repo)
        test_db.commit()
        
        # Create existing issue
        issue = Issue(
            repo_id=repo.id,
            number=1,
            title="Bug report",
            state="open",
            author="testuser",
            labels_json="[]",
            assignees_json="[]",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(issue)
        test_db.commit()
        
        # Update payload for closed action
        sample_issue_payload["action"] = "closed"
        sample_issue_payload["issue"]["state"] = "closed"
        sample_issue_payload["issue"]["closed_at"] = "2024-01-02T12:00:00Z"
        
        result = await webhook_handler.process_issues_event(test_db, sample_issue_payload, repo)
        test_db.commit()  # Commit the changes
        
        test_db.refresh(issue)
        assert issue.state == "closed"
        assert issue.closed_at is not None


class TestEventStorage:
    """Test event storage in database"""

    @pytest.mark.asyncio
    async def test_event_stored(self, webhook_handler, test_db, sample_push_payload):
        """Test that events are stored in database"""
        repo = Repository(
            full_name="testuser/test-repo",
            name="test-repo",
            owner="testuser",
            default_branch="main",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        test_db.add(repo)
        test_db.commit()
        
        # Manually store event (simulating what handle_webhook does)
        event = Event(
            repo_id=repo.id,
            event_type="push",
            action=None,
            payload_json=json.dumps(sample_push_payload),
            delivery_id="test-delivery-123",
            actor="testuser",
            created_at=datetime.utcnow()
        )
        test_db.add(event)
        test_db.commit()
        
        stored_event = test_db.query(Event).filter(
            Event.delivery_id == "test-delivery-123"
        ).first()
        
        assert stored_event is not None
        assert stored_event.event_type == "push"
        assert stored_event.actor == "testuser"


class TestDiscordNotification:
    """Test Discord notification functionality"""

    @pytest.mark.asyncio
    async def test_discord_notification_force_push(self, webhook_handler):
        """Test Discord notification for force push"""
        payload = {
            "ref": "refs/heads/main",
            "forced": True,
            "commits": [{"id": "abc123"}] * 5,
            "repository": {
                "default_branch": "main"
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_post = AsyncMock()
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            await webhook_handler.send_discord_notification("push", payload, "testuser/test-repo")
            
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "Force push" in call_args[1]["json"]["content"]

    @pytest.mark.asyncio
    async def test_discord_notification_pr_opened(self, webhook_handler):
        """Test Discord notification for PR opened"""
        payload = {
            "action": "opened",
            "pull_request": {
                "number": 42,
                "title": "Amazing feature"
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_post = AsyncMock()
            mock_client.return_value.__aenter__.return_value.post = mock_post
            
            await webhook_handler.send_discord_notification("pull_request", payload, "testuser/test-repo")
            
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert "PR opened" in call_args[1]["json"]["content"]
            assert "#42" in call_args[1]["json"]["content"]


class TestDateTimeParsing:
    """Test datetime parsing utility"""

    def test_parse_datetime_valid(self, webhook_handler):
        """Test parsing valid datetime string"""
        dt_string = "2024-01-01T12:00:00Z"
        result = webhook_handler._parse_datetime(dt_string)
        
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1

    def test_parse_datetime_none(self, webhook_handler):
        """Test parsing None datetime"""
        result = webhook_handler._parse_datetime(None)
        assert result is None

    def test_parse_datetime_invalid(self, webhook_handler):
        """Test parsing invalid datetime string"""
        result = webhook_handler._parse_datetime("invalid-date")
        assert result is None
