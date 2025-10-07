# Webhook Test Samples

## Push Event Test

```bash
curl -X POST http://localhost:9000/api/github/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-GitHub-Delivery: 12345-67890-abcdef" \
  -H "X-Hub-Signature-256: sha256=your_signature_here" \
  -d '{
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
      "clone_url": "https://github.com/testuser/test-repo.git",
      "ssh_url": "git@github.com:testuser/test-repo.git",
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
  }'
```

## Pull Request Event Test

```bash
curl -X POST http://localhost:9000/api/github/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -H "X-GitHub-Delivery: 12345-67890-abcdef" \
  -H "X-Hub-Signature-256: sha256=your_signature_here" \
  -d '{
    "action": "opened",
    "number": 1,
    "pull_request": {
      "id": 987654321,
      "number": 1,
      "title": "Add new feature",
      "body": "This PR adds a new feature to the application.",
      "state": "open",
      "draft": false,
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
      "mergeable": true,
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
  }'
```

## Issues Event Test

```bash
curl -X POST http://localhost:9000/api/github/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: issues" \
  -H "X-GitHub-Delivery: 12345-67890-abcdef" \
  -H "X-Hub-Signature-256: sha256=your_signature_here" \
  -d '{
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
      "milestone": null,
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
  }'
```

## Workflow Run Event Test

```bash
curl -X POST http://localhost:9000/api/github/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: workflow_run" \
  -H "X-GitHub-Delivery: 12345-67890-abcdef" \
  -H "X-Hub-Signature-256: sha256=your_signature_here" \
  -d '{
    "action": "completed",
    "workflow_run": {
      "id": 888999000,
      "name": "CI",
      "workflow_id": 111222333,
      "status": "completed",
      "conclusion": "success",
      "head_branch": "main",
      "head_sha": "1234567890abcdef1234567890abcdef12345678",
      "event": "push",
      "actor": {
        "login": "testuser",
        "id": 12345
      },
      "html_url": "https://github.com/testuser/test-repo/actions/runs/888999000",
      "jobs_url": "https://api.github.com/repos/testuser/test-repo/actions/runs/888999000/jobs",
      "logs_url": "https://api.github.com/repos/testuser/test-repo/actions/runs/888999000/logs",
      "run_started_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-01T12:05:00Z"
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
  }'
```

## API Test Commands

### Get Repositories
```bash
curl http://localhost:9000/api/repos
```

### Get Statistics
```bash
curl http://localhost:9000/api/stats
```

### Get Recent Events
```bash
curl http://localhost:9000/api/events?limit=10
```

### Manual GitHub Sync
```bash
curl -X POST http://localhost:9000/api/sync/github
```

### Health Check
```bash
curl http://localhost:9000/health
```

## Signature Generation (for testing)

If you need to generate a valid signature for testing:

```python
import hmac
import hashlib
import json

def generate_signature(payload, secret):
    payload_bytes = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    signature = hmac.new(
        secret.encode('utf-8'),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"

# Example usage
payload = {"zen": "Non-blocking is better than blocking."}
secret = "your_webhook_secret_here"
signature = generate_signature(payload, secret)
print(signature)
```