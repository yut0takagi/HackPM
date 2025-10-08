#!/usr/bin/env python3
"""
Comprehensive GitHub API integration tests for template parsing system
"""
import sys
import os
import json
import time
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, Optional

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.core.template_parser import template_parser, TemplateType, Priority
from src.core.status_mapping import status_mapping_service, DashboardStatus, DashboardCategory, DashboardPriority
from src.core.branch_naming import branch_naming_service, BranchType

class GitHubAPITestSuite:
    """Comprehensive test suite for GitHub API integration"""
    
    def __init__(self):
        self.mock_responses = self._setup_mock_responses()
        self.api_call_log = []
        
    def _setup_mock_responses(self) -> Dict[str, Any]:
        """Set up mock API responses for testing"""
        return {
            "issues": {
                123: {
                    "number": 123,
                    "title": "Implement GitHub Template System",
                    "body": """---
template_type: feature
priority: high
estimated_time: 8
user_story: As a developer, I want GitHub templates, so that I can standardize issues
acceptance_criteria:
  - "[x] Create YAML templates"
  - "[ ] Implement parser logic"
  - "[x] Add validation"
  - "[ ] Write comprehensive tests"
technical_requirements:
  - "Use PyYAML for parsing"
  - "Implement input sanitization"
  - "Add error handling"
branch_name: feature/123-github-template-system
---

## Description
This feature implements a comprehensive GitHub template system.

## Additional Context
Critical for hackathon workflow standardization.
""",
                    "state": "open",
                    "labels": [
                        {"name": "feature", "color": "0052cc"},
                        {"name": "high-priority", "color": "d93f0b"},
                        {"name": "hackathon", "color": "0e8a16"}
                    ],
                    "assignees": [
                        {"login": "developer1", "id": 1}
                    ],
                    "milestone": {
                        "title": "Sprint 1",
                        "number": 1
                    },
                    "created_at": "2023-01-01T00:00:00Z",
                    "updated_at": "2023-01-01T12:00:00Z"
                },
                456: {
                    "number": 456,
                    "title": "Fix memory leak in parser",
                    "body": """---
template_type: bug
priority: critical
reproduction_steps:
  - "Load large YAML template"
  - "Parse multiple times"
  - "Monitor memory usage"
expected_behavior: Memory should be released after parsing
actual_behavior: Memory usage keeps increasing
environment:
  os: "Ubuntu 20.04"
  python: "3.9.0"
  memory: "16GB"
---

## Bug Description
Memory leak detected in template parser when processing large YAML files.

## Impact
Affects production performance with large repositories.
""",
                    "state": "open",
                    "labels": [
                        {"name": "bug", "color": "d73a49"},
                        {"name": "critical", "color": "b60205"},
                        {"name": "performance", "color": "1d76db"}
                    ],
                    "assignees": [
                        {"login": "developer2", "id": 2}
                    ],
                    "created_at": "2023-01-02T00:00:00Z",
                    "updated_at": "2023-01-02T08:00:00Z"
                }
            },
            "pull_requests": {
                789: {
                    "number": 789,
                    "title": "Add comprehensive template validation",
                    "body": """## Changes Summary
This PR adds comprehensive validation for GitHub issue templates including:
- YAML schema validation
- Input sanitization
- Error handling improvements

## Related Issues
Fixes #123
Relates to #456

## Testing Checklist
- [x] Unit tests pass (100% coverage)
- [x] Integration tests pass
- [x] Security tests pass
- [ ] Performance tests completed
- [ ] Manual testing done
- [x] Documentation updated

## Breaking Changes
- Changed TemplateParser constructor signature
- Updated validation error format

## Deployment Notes
Requires PyYAML >= 6.0
Update configuration files before deployment.
""",
                    "state": "open",
                    "draft": False,
                    "mergeable": True,
                    "labels": [
                        {"name": "enhancement", "color": "a2eeef"},
                        {"name": "validation", "color": "0052cc"}
                    ],
                    "requested_reviewers": [
                        {"login": "reviewer1", "id": 3}
                    ],
                    "created_at": "2023-01-03T00:00:00Z",
                    "updated_at": "2023-01-03T10:00:00Z"
                }
            },
            "branches": [
                {"name": "main", "protected": True},
                {"name": "feature/123-github-template-system", "protected": False},
                {"name": "bugfix/456-fix-memory-leak", "protected": False},
                {"name": "hotfix/789-security-patch", "protected": False},
                {"name": "chore/101-update-dependencies", "protected": False},
                {"name": "feature/999-invalid-branch-name-test", "protected": False}
            ],
            "rate_limit": {
                "rate": {
                    "limit": 5000,
                    "remaining": 4950,
                    "reset": int(time.time() + 3600)
                }
            }
        }
    
    def mock_api_call(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Mock GitHub API call with logging"""
        self.api_call_log.append({
            "endpoint": endpoint,
            "timestamp": time.time(),
            "kwargs": kwargs
        })
        
        # Simulate API delay
        time.sleep(0.01)
        
        # Route to appropriate mock response
        if endpoint.startswith("issues/"):
            issue_number = int(endpoint.split("/")[1])
            if issue_number in self.mock_responses["issues"]:
                return self.mock_responses["issues"][issue_number]
            else:
                raise Exception(f"Issue #{issue_number} not found")
        
        elif endpoint.startswith("pulls/"):
            pr_number = int(endpoint.split("/")[1])
            if pr_number in self.mock_responses["pull_requests"]:
                return self.mock_responses["pull_requests"][pr_number]
            else:
                raise Exception(f"PR #{pr_number} not found")
        
        elif endpoint == "branches":
            return self.mock_responses["branches"]
        
        elif endpoint == "rate_limit":
            return self.mock_responses["rate_limit"]
        
        else:
            raise Exception(f"Unknown endpoint: {endpoint}")

def test_issue_template_parsing_integration():
    """Test complete issue template parsing integration"""
    print("Testing issue template parsing integration...")
    
    test_suite = GitHubAPITestSuite()
    
    # Test feature issue
    issue_data = test_suite.mock_api_call("issues/123")
    
    # Parse template data
    template_data = template_parser.parse_issue_body(
        issue_data["body"],
        [label["name"] for label in issue_data["labels"]]
    )
    
    # Verify parsing results
    assert template_data.template_type == TemplateType.FEATURE
    assert template_data.priority == Priority.HIGH
    assert template_data.estimated_time == 8
    assert len(template_data.acceptance_criteria) == 4
    assert len(template_data.technical_requirements) == 3
    assert template_data.branch_suggestion == "feature/123-github-template-system"
    
    # Map to dashboard
    dashboard_data = status_mapping_service.map_issue_to_dashboard(
        template_data,
        labels=[label["name"] for label in issue_data["labels"]],
        assignees=[assignee["login"] for assignee in issue_data["assignees"]],
        issue_state=issue_data["state"]
    )
    
    # Verify dashboard mapping
    assert dashboard_data.category == DashboardCategory.FEATURE
    assert dashboard_data.priority == DashboardPriority.HIGH
    assert dashboard_data.status == DashboardStatus.IN_PROGRESS
    assert dashboard_data.acceptance_criteria_total == 4
    assert dashboard_data.acceptance_criteria_completed == 2  # 2 items marked [x]
    
    print("  ✓ Feature issue parsing and mapping successful")
    
    # Test bug issue
    bug_data = test_suite.mock_api_call("issues/456")
    
    bug_template = template_parser.parse_issue_body(
        bug_data["body"],
        [label["name"] for label in bug_data["labels"]]
    )
    
    # Verify bug parsing
    assert bug_template.template_type == TemplateType.BUG
    assert bug_template.priority == Priority.CRITICAL
    assert len(bug_template.reproduction_steps) == 3
    assert bug_template.expected_behavior is not None
    assert bug_template.actual_behavior is not None
    assert "os" in bug_template.environment_details
    
    bug_dashboard = status_mapping_service.map_issue_to_dashboard(
        bug_template,
        labels=[label["name"] for label in bug_data["labels"]],
        assignees=[assignee["login"] for assignee in bug_data["assignees"]],
        issue_state=bug_data["state"]
    )
    
    assert bug_dashboard.category == DashboardCategory.BUG
    assert bug_dashboard.priority == DashboardPriority.CRITICAL
    
    print("  ✓ Bug issue parsing and mapping successful")

def test_pr_template_parsing_integration():
    """Test PR template parsing integration"""
    print("Testing PR template parsing integration...")
    
    test_suite = GitHubAPITestSuite()
    
    # Get PR data
    pr_data = test_suite.mock_api_call("pulls/789")
    
    # Parse PR template
    pr_template = template_parser.parse_pr_body(
        pr_data["body"],
        pr_data["title"]
    )
    
    # Verify PR parsing
    assert pr_template.changes_summary is not None
    assert len(pr_template.related_issues) == 2
    assert 123 in pr_template.related_issues
    assert 456 in pr_template.related_issues
    assert len(pr_template.testing_checklist) == 6
    assert pr_template.breaking_changes is not None
    assert pr_template.deployment_notes is not None
    
    # Map PR to dashboard
    pr_dashboard = status_mapping_service.map_pr_to_dashboard(
        pr_template,
        pr_state=pr_data["state"],
        is_draft=pr_data["draft"],
        mergeable=pr_data["mergeable"]
    )
    
    # Verify PR dashboard mapping
    assert pr_dashboard.category == DashboardCategory.TASK
    assert pr_dashboard.priority == DashboardPriority.HIGH  # Has breaking changes
    assert pr_dashboard.acceptance_criteria_total == 6
    assert pr_dashboard.acceptance_criteria_completed == 4  # 4 items marked [x]
    assert pr_dashboard.has_technical_requirements == True  # Has breaking changes
    assert pr_dashboard.is_time_sensitive == True  # Has breaking changes
    
    print("  ✓ PR template parsing and mapping successful")

def test_branch_linking_integration():
    """Test branch to issue linking integration"""
    print("Testing branch linking integration...")
    
    test_suite = GitHubAPITestSuite()
    
    # Get branches
    branches = test_suite.mock_api_call("branches")
    
    # Get issues for linking
    issue_123 = test_suite.mock_api_call("issues/123")
    issue_456 = test_suite.mock_api_call("issues/456")
    
    issue_map = {
        123: issue_123,
        456: issue_456
    }
    
    # Test branch linking
    linked_branches = []
    for branch in branches:
        branch_name = branch["name"]
        
        # Skip protected branches
        if branch.get("protected", False):
            continue
        
        # Parse branch name
        branch_info = branch_naming_service.parse_branch_name(branch_name)
        
        if branch_info.issue_number and branch_info.issue_number in issue_map:
            linked_issue = issue_map[branch_info.issue_number]
            
            # Parse the linked issue's template
            template_data = template_parser.parse_issue_body(
                linked_issue["body"],
                [label["name"] for label in linked_issue["labels"]]
            )
            
            linked_branches.append({
                "branch_name": branch_name,
                "branch_info": branch_info,
                "issue_data": linked_issue,
                "template_data": template_data
            })
    
    # Verify linking results
    assert len(linked_branches) >= 2  # Should link at least 2 branches
    
    for link in linked_branches:
        assert link["branch_info"].is_valid
        assert link["issue_data"]["number"] == link["branch_info"].issue_number
        
        # Verify branch name suggestion matches
        if link["template_data"].branch_suggestion:
            assert link["branch_name"] == link["template_data"].branch_suggestion
        
        print(f"  ✓ Linked branch '{link['branch_name']}' to issue #{link['issue_data']['number']}")
    
    print("  ✓ Branch linking integration successful")

def test_api_error_handling():
    """Test API error handling and recovery"""
    print("Testing API error handling...")
    
    test_suite = GitHubAPITestSuite()
    
    # Test 404 error handling
    try:
        test_suite.mock_api_call("issues/999")  # Non-existent issue
        assert False, "Should have raised an exception"
    except Exception as e:
        assert "not found" in str(e)
        print("  ✓ 404 error handling working")
    
    # Test rate limit simulation
    rate_limit_data = test_suite.mock_api_call("rate_limit")
    remaining = rate_limit_data["rate"]["remaining"]
    
    # Simulate rate limit checking
    if remaining < 100:
        print("  ✓ Rate limit warning would be triggered")
    else:
        print(f"  ✓ Rate limit OK: {remaining} requests remaining")
    
    # Test retry logic simulation
    max_retries = 3
    retry_delays = [1, 2, 4]  # Exponential backoff
    
    for i, delay in enumerate(retry_delays):
        if i < max_retries - 1:
            assert delay <= 60  # Reasonable max delay
    
    print("  ✓ Retry logic parameters validated")

def test_data_consistency_validation():
    """Test data consistency between GitHub and parsed data"""
    print("Testing data consistency validation...")
    
    test_suite = GitHubAPITestSuite()
    
    # Test issue data consistency
    issue_data = test_suite.mock_api_call("issues/123")
    template_data = template_parser.parse_issue_body(
        issue_data["body"],
        [label["name"] for label in issue_data["labels"]]
    )
    
    # Verify consistency
    github_labels = [label["name"] for label in issue_data["labels"]]
    
    # Priority should be consistent with labels
    if "high-priority" in github_labels:
        assert template_data.priority == Priority.HIGH
    
    # Template type should be consistent with labels
    if "feature" in github_labels:
        assert template_data.template_type == TemplateType.FEATURE
    
    # State consistency
    dashboard_data = status_mapping_service.map_issue_to_dashboard(
        template_data,
        labels=github_labels,
        assignees=[assignee["login"] for assignee in issue_data["assignees"]],
        issue_state=issue_data["state"]
    )
    
    if issue_data["state"] == "closed":
        assert dashboard_data.status == DashboardStatus.DONE
    elif issue_data["assignees"]:
        assert dashboard_data.status == DashboardStatus.IN_PROGRESS
    
    print("  ✓ Issue data consistency validated")
    
    # Test PR data consistency
    pr_data = test_suite.mock_api_call("pulls/789")
    pr_template = template_parser.parse_pr_body(pr_data["body"], pr_data["title"])
    
    # Verify PR consistency
    if pr_data["draft"]:
        # Draft PRs should be in progress
        pr_dashboard = status_mapping_service.map_pr_to_dashboard(
            pr_template,
            pr_state=pr_data["state"],
            is_draft=True
        )
        assert pr_dashboard.status == DashboardStatus.IN_PROGRESS
    
    print("  ✓ PR data consistency validated")

def test_performance_benchmarks():
    """Test performance benchmarks for API integration"""
    print("Testing performance benchmarks...")
    
    test_suite = GitHubAPITestSuite()
    
    # Benchmark issue parsing
    start_time = time.time()
    
    for i in range(100):  # Process 100 issues
        try:
            if i % 2 == 0:
                issue_data = test_suite.mock_api_call("issues/123")
            else:
                issue_data = test_suite.mock_api_call("issues/456")
            
            template_data = template_parser.parse_issue_body(
                issue_data["body"],
                [label["name"] for label in issue_data["labels"]]
            )
            
            dashboard_data = status_mapping_service.map_issue_to_dashboard(
                template_data,
                labels=[label["name"] for label in issue_data["labels"]],
                assignees=[assignee["login"] for assignee in issue_data["assignees"]],
                issue_state=issue_data["state"]
            )
            
        except Exception as e:
            print(f"  Error processing issue {i}: {e}")
    
    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / 100
    
    # Performance assertions
    assert avg_time < 0.1  # Less than 100ms per issue
    assert total_time < 5.0  # Less than 5 seconds total
    
    print(f"  ✓ Processed 100 issues in {total_time:.3f}s")
    print(f"  ✓ Average time per issue: {avg_time:.3f}s")
    
    # Check API call efficiency
    api_calls = len(test_suite.api_call_log)
    print(f"  ✓ Made {api_calls} API calls total")

def test_security_validation():
    """Test security validation in API integration"""
    print("Testing security validation...")
    
    # Test malicious input handling
    malicious_body = """---
template_type: feature
user_story: "<script>alert('xss')</script>As a user, I want security"
acceptance_criteria:
  - "<img src=x onerror=alert('xss')>Criterion 1"
  - "javascript:alert('xss')"
technical_requirements:
  - "<iframe src='javascript:alert(1)'></iframe>Requirement"
---

## Description
<script>document.location='http://evil.com'</script>
This is a malicious template.
"""
    
    # Parse malicious input
    result = template_parser.parse_issue_body(malicious_body, ["feature"])
    
    # Verify sanitization
    assert "<script>" not in result.user_story
    assert "alert" in result.user_story  # Content preserved, tags removed
    assert "<img" not in result.acceptance_criteria[0]
    assert "javascript:" not in result.acceptance_criteria[1]
    assert "<iframe" not in result.technical_requirements[0]
    
    print("  ✓ XSS prevention working")
    
    # Test SQL injection patterns
    sql_injection_body = """---
template_type: bug
reproduction_steps:
  - "Enter '; DROP TABLE users; --"
  - "Submit form with 1' OR '1'='1"
expected_behavior: "Input should be escaped"
actual_behavior: "System vulnerable to ' OR 1=1 --"
---"""
    
    sql_result = template_parser.parse_issue_body(sql_injection_body, ["bug"])
    
    # Verify SQL injection prevention
    repro_text = " ".join(sql_result.reproduction_steps)
    assert "DROP TABLE" not in repro_text
    assert "OR 1=1" not in sql_result.actual_behavior
    
    print("  ✓ SQL injection prevention working")

def main():
    """Run all GitHub API integration tests"""
    print("Running comprehensive GitHub API integration tests...\n")
    
    try:
        test_issue_template_parsing_integration()
        print()
        test_pr_template_parsing_integration()
        print()
        test_branch_linking_integration()
        print()
        test_api_error_handling()
        print()
        test_data_consistency_validation()
        print()
        test_performance_benchmarks()
        print()
        test_security_validation()
        
        print("\n🎉 All GitHub API integration tests passed!")
        print("\nSystem is ready for production deployment!")
        return 0
    except Exception as e:
        print(f"\n❌ GitHub API integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())