#!/usr/bin/env python3
"""
End-to-end workflow testing for GitHub template system
Tests complete workflows from issue creation to dashboard display
"""
import sys
import os
import json
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.core.template_parser import template_parser, TemplateType, Priority, ParsedTemplateData
from src.core.status_mapping import status_mapping_service, DashboardStatus, DashboardCategory, DashboardPriority
from src.core.branch_naming import branch_naming_service, BranchType

@dataclass
class WorkflowStep:
    """Represents a step in the workflow"""
    name: str
    action: str
    data: Dict[str, Any]
    expected_result: Dict[str, Any]
    timestamp: float

class EndToEndWorkflowTester:
    """End-to-end workflow testing framework"""
    
    def __init__(self):
        self.workflow_log = []
        self.dashboard_state = {}
        self.github_state = {
            "issues": {},
            "pull_requests": {},
            "branches": {},
            "repositories": {}
        }
        
    def log_step(self, step: WorkflowStep):
        """Log a workflow step"""
        self.workflow_log.append(step)
        
    def simulate_github_issue_creation(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate GitHub issue creation"""
        issue_number = issue_data.get("number", len(self.github_state["issues"]) + 1)
        
        created_issue = {
            "number": issue_number,
            "title": issue_data["title"],
            "body": issue_data["body"],
            "state": "open",
            "labels": issue_data.get("labels", []),
            "assignees": issue_data.get("assignees", []),
            "milestone": issue_data.get("milestone"),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        self.github_state["issues"][issue_number] = created_issue
        
        self.log_step(WorkflowStep(
            name="GitHub Issue Creation",
            action="create_issue",
            data=issue_data,
            expected_result={"issue_number": issue_number},
            timestamp=time.time()
        ))
        
        return created_issue
    
    def simulate_template_parsing(self, issue_data: Dict[str, Any]) -> ParsedTemplateData:
        """Simulate template parsing"""
        template_data = template_parser.parse_issue_body(
            issue_data["body"],
            [label["name"] if isinstance(label, dict) else label for label in issue_data.get("labels", [])]
        )
        
        self.log_step(WorkflowStep(
            name="Template Parsing",
            action="parse_template",
            data={"issue_number": issue_data["number"]},
            expected_result={
                "template_type": template_data.template_type.value,
                "priority": template_data.priority.value,
                "criteria_count": len(template_data.acceptance_criteria or [])
            },
            timestamp=time.time()
        ))
        
        return template_data
    
    def simulate_dashboard_mapping(self, template_data: ParsedTemplateData, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate dashboard mapping"""
        dashboard_data = status_mapping_service.map_issue_to_dashboard(
            template_data,
            labels=[label["name"] if isinstance(label, dict) else label for label in issue_data.get("labels", [])],
            assignees=[assignee["login"] if isinstance(assignee, dict) else assignee for assignee in issue_data.get("assignees", [])],
            issue_state=issue_data["state"]
        )
        
        # Store in dashboard state
        self.dashboard_state[issue_data["number"]] = {
            "category": dashboard_data.category.value,
            "priority": dashboard_data.priority.value,
            "status": dashboard_data.status.value,
            "progress": dashboard_data.progress_percentage,
            "acceptance_criteria_total": dashboard_data.acceptance_criteria_total,
            "acceptance_criteria_completed": dashboard_data.acceptance_criteria_completed,
            "estimated_hours": dashboard_data.estimated_hours,
            "is_time_sensitive": dashboard_data.is_time_sensitive
        }
        
        self.log_step(WorkflowStep(
            name="Dashboard Mapping",
            action="map_to_dashboard",
            data={"issue_number": issue_data["number"]},
            expected_result=self.dashboard_state[issue_data["number"]],
            timestamp=time.time()
        ))
        
        return self.dashboard_state[issue_data["number"]]
    
    def simulate_branch_creation(self, issue_data: Dict[str, Any], template_data: ParsedTemplateData) -> Dict[str, Any]:
        """Simulate branch creation based on issue"""
        # Use suggested branch name from template or generate one
        if template_data.branch_suggestion:
            branch_name = template_data.branch_suggestion
        else:
            branch_type = BranchType.FEATURE
            if template_data.template_type == TemplateType.BUG:
                branch_type = BranchType.BUGFIX
            elif template_data.template_type == TemplateType.TASK:
                branch_type = BranchType.CHORE
            
            branch_name = branch_naming_service.suggest_branch_name(
                issue_data["number"],
                issue_data["title"],
                branch_type
            )
        
        # Validate branch name
        is_valid, errors = branch_naming_service.validate_branch_name(branch_name)
        
        branch_data = {
            "name": branch_name,
            "is_valid": is_valid,
            "validation_errors": errors,
            "linked_issue": issue_data["number"],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        self.github_state["branches"][branch_name] = branch_data
        
        self.log_step(WorkflowStep(
            name="Branch Creation",
            action="create_branch",
            data={"branch_name": branch_name, "issue_number": issue_data["number"]},
            expected_result={"is_valid": is_valid, "linked": True},
            timestamp=time.time()
        ))
        
        return branch_data
    
    def simulate_pr_creation(self, branch_data: Dict[str, Any], pr_template_body: str) -> Dict[str, Any]:
        """Simulate PR creation"""
        pr_number = len(self.github_state["pull_requests"]) + 1
        
        pr_data = {
            "number": pr_number,
            "title": f"PR for {branch_data['name']}",
            "body": pr_template_body,
            "state": "open",
            "draft": False,
            "mergeable": True,
            "head": {"ref": branch_data["name"]},
            "base": {"ref": "main"},
            "labels": [],
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        self.github_state["pull_requests"][pr_number] = pr_data
        
        # Parse PR template
        pr_template_data = template_parser.parse_pr_body(pr_template_body, pr_data["title"])
        
        self.log_step(WorkflowStep(
            name="PR Creation",
            action="create_pr",
            data={"pr_number": pr_number, "branch": branch_data["name"]},
            expected_result={
                "pr_number": pr_number,
                "related_issues": pr_template_data.related_issues or []
            },
            timestamp=time.time()
        ))
        
        return pr_data
    
    def simulate_issue_update(self, issue_number: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate issue update (status change, assignment, etc.)"""
        if issue_number not in self.github_state["issues"]:
            raise ValueError(f"Issue #{issue_number} not found")
        
        issue = self.github_state["issues"][issue_number]
        
        # Apply updates
        for key, value in updates.items():
            if key == "assignees" and value:
                issue["assignees"] = [{"login": assignee} if isinstance(assignee, str) else assignee for assignee in value]
            elif key == "labels" and value:
                issue["labels"] = [{"name": label} if isinstance(label, str) else label for label in value]
            else:
                issue[key] = value
        
        issue["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        self.log_step(WorkflowStep(
            name="Issue Update",
            action="update_issue",
            data={"issue_number": issue_number, "updates": updates},
            expected_result={"updated": True},
            timestamp=time.time()
        ))
        
        return issue
    
    def verify_dashboard_sync(self, issue_number: int) -> bool:
        """Verify dashboard is synchronized with GitHub state"""
        if issue_number not in self.github_state["issues"]:
            return False
        
        if issue_number not in self.dashboard_state:
            return False
        
        github_issue = self.github_state["issues"][issue_number]
        dashboard_issue = self.dashboard_state[issue_number]
        
        # Re-parse and re-map to get current state
        template_data = self.simulate_template_parsing(github_issue)
        current_dashboard = self.simulate_dashboard_mapping(template_data, github_issue)
        
        # Check if dashboard state matches current GitHub state
        return current_dashboard == dashboard_issue
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        """Get summary of workflow execution"""
        return {
            "total_steps": len(self.workflow_log),
            "github_issues": len(self.github_state["issues"]),
            "github_prs": len(self.github_state["pull_requests"]),
            "github_branches": len(self.github_state["branches"]),
            "dashboard_items": len(self.dashboard_state),
            "execution_time": self.workflow_log[-1].timestamp - self.workflow_log[0].timestamp if self.workflow_log else 0,
            "steps": [{"name": step.name, "action": step.action, "timestamp": step.timestamp} for step in self.workflow_log]
        }

def test_complete_feature_workflow():
    """Test complete feature development workflow"""
    print("Testing complete feature development workflow...")
    
    tester = EndToEndWorkflowTester()
    
    # Step 1: Create feature issue with template
    feature_issue_data = {
        "title": "Implement user authentication system",
        "body": """---
template_type: feature
priority: high
estimated_time: 16
user_story: As a user, I want to log in securely, so that I can access my account
acceptance_criteria:
  - "[ ] User can register with email and password"
  - "[ ] User can log in with valid credentials"
  - "[x] Password validation is implemented"
  - "[ ] Session management works correctly"
  - "[ ] Logout functionality is available"
technical_requirements:
  - "Implement JWT token authentication"
  - "Add password hashing with bcrypt"
  - "Create user database schema"
  - "Add input validation and sanitization"
branch_name: feature/100-user-authentication-system
---

## Description
Implement a comprehensive user authentication system with secure login/logout functionality.

## Security Requirements
- Passwords must be hashed
- JWT tokens for session management
- Input validation to prevent injection attacks

## Acceptance Criteria Details
The system should handle user registration, login, and session management securely.
""",
        "labels": ["feature", "high-priority", "security", "authentication"],
        "assignees": []
    }
    
    # Create the issue
    github_issue = tester.simulate_github_issue_creation(feature_issue_data)
    assert github_issue["number"] == 1
    print("  ✓ Feature issue created")
    
    # Step 2: Parse template
    template_data = tester.simulate_template_parsing(github_issue)
    assert template_data.template_type == TemplateType.FEATURE
    assert template_data.priority == Priority.HIGH
    assert template_data.estimated_time == 16
    assert len(template_data.acceptance_criteria) == 5
    assert len(template_data.technical_requirements) == 4
    print("  ✓ Template parsed successfully")
    
    # Step 3: Map to dashboard
    dashboard_data = tester.simulate_dashboard_mapping(template_data, github_issue)
    assert dashboard_data["category"] == "feature"
    assert dashboard_data["priority"] == "high"
    assert dashboard_data["status"] == "todo"  # No assignees yet
    assert dashboard_data["acceptance_criteria_total"] == 5
    assert dashboard_data["acceptance_criteria_completed"] == 1  # One marked [x]
    print("  ✓ Dashboard mapping successful")
    
    # Step 4: Assign developer and update status
    updated_issue = tester.simulate_issue_update(1, {
        "assignees": ["developer1"],
        "labels": ["feature", "high-priority", "security", "authentication", "in-progress"]
    })
    
    # Re-map to dashboard to reflect assignment
    updated_template = tester.simulate_template_parsing(updated_issue)
    updated_dashboard = tester.simulate_dashboard_mapping(updated_template, updated_issue)
    assert updated_dashboard["status"] == "in-progress"
    print("  ✓ Issue assignment and status update successful")
    
    # Step 5: Create branch
    branch_data = tester.simulate_branch_creation(github_issue, template_data)
    assert branch_data["is_valid"] == True
    assert branch_data["name"] == "feature/100-user-authentication-system"
    assert branch_data["linked_issue"] == 1
    print("  ✓ Branch created and linked")
    
    # Step 6: Create PR
    pr_body = """## Changes Summary
This PR implements the user authentication system with the following features:
- User registration with email validation
- Secure login with JWT tokens
- Password hashing with bcrypt
- Session management
- Logout functionality

## Related Issues
Fixes #1

## Testing Checklist
- [x] Unit tests for authentication logic
- [x] Integration tests for API endpoints
- [x] Security tests for password handling
- [ ] Manual testing of user flows
- [ ] Performance testing under load

## Breaking Changes
None - this is a new feature.

## Deployment Notes
- Run database migrations to create user tables
- Update environment variables for JWT secret
- Install bcrypt dependency
"""
    
    pr_data = tester.simulate_pr_creation(branch_data, pr_body)
    assert pr_data["number"] == 1
    print("  ✓ PR created")
    
    # Step 7: Update issue to reflect PR creation
    pr_linked_issue = tester.simulate_issue_update(1, {
        "labels": ["feature", "high-priority", "security", "authentication", "review"]
    })
    
    # Re-map to dashboard
    pr_template = tester.simulate_template_parsing(pr_linked_issue)
    pr_dashboard = tester.simulate_dashboard_mapping(pr_template, pr_linked_issue)
    assert pr_dashboard["status"] == "review"
    print("  ✓ Issue status updated to review")
    
    # Step 8: Complete some acceptance criteria
    completed_issue = tester.simulate_issue_update(1, {
        "body": github_issue["body"].replace(
            "[ ] User can register with email and password",
            "[x] User can register with email and password"
        ).replace(
            "[ ] User can log in with valid credentials",
            "[x] User can log in with valid credentials"
        )
    })
    
    # Re-parse and verify progress
    completed_template = tester.simulate_template_parsing(completed_issue)
    completed_dashboard = tester.simulate_dashboard_mapping(completed_template, completed_issue)
    assert completed_dashboard["acceptance_criteria_completed"] == 3  # Now 3 completed
    print("  ✓ Acceptance criteria progress updated")
    
    # Step 9: Close issue
    closed_issue = tester.simulate_issue_update(1, {"state": "closed"})
    closed_template = tester.simulate_template_parsing(closed_issue)
    closed_dashboard = tester.simulate_dashboard_mapping(closed_template, closed_issue)
    assert closed_dashboard["status"] == "done"
    print("  ✓ Issue closed and marked as done")
    
    # Verify workflow summary
    summary = tester.get_workflow_summary()
    assert summary["total_steps"] >= 8
    assert summary["github_issues"] == 1
    assert summary["github_prs"] == 1
    assert summary["github_branches"] == 1
    assert summary["dashboard_items"] == 1
    
    print(f"  ✓ Workflow completed in {summary['execution_time']:.3f} seconds")
    print("  ✓ Complete feature workflow test passed")

def test_bug_fix_workflow():
    """Test bug fix workflow"""
    print("Testing bug fix workflow...")
    
    tester = EndToEndWorkflowTester()
    
    # Step 1: Create bug issue
    bug_issue_data = {
        "title": "Memory leak in template parser",
        "body": """---
template_type: bug
priority: critical
reproduction_steps:
  - "Load large YAML template (>1MB)"
  - "Parse template multiple times in loop"
  - "Monitor memory usage with htop"
  - "Observe memory not being released"
expected_behavior: Memory should be released after parsing completes
actual_behavior: Memory usage increases with each parse and is never released
environment:
  os: "Ubuntu 20.04"
  python: "3.9.0"
  memory: "16GB"
  template_size: "1.2MB"
---

## Bug Description
Critical memory leak discovered in template parser when processing large YAML files repeatedly.

## Impact
- Production servers running out of memory
- Performance degradation over time
- Potential service crashes

## Debugging Information
Memory profiling shows objects not being garbage collected after parsing.
""",
        "labels": ["bug", "critical", "memory-leak", "performance"],
        "assignees": ["senior-developer"]
    }
    
    # Create bug issue
    bug_issue = tester.simulate_github_issue_creation(bug_issue_data)
    print("  ✓ Bug issue created")
    
    # Parse and map
    bug_template = tester.simulate_template_parsing(bug_issue)
    assert bug_template.template_type == TemplateType.BUG
    assert bug_template.priority == Priority.CRITICAL
    assert len(bug_template.reproduction_steps) == 4
    assert bug_template.expected_behavior is not None
    assert bug_template.actual_behavior is not None
    
    bug_dashboard = tester.simulate_dashboard_mapping(bug_template, bug_issue)
    assert bug_dashboard["category"] == "bug"
    assert bug_dashboard["priority"] == "critical"
    assert bug_dashboard["status"] == "in-progress"  # Has assignee
    print("  ✓ Bug template parsed and mapped")
    
    # Create bugfix branch
    bugfix_branch = tester.simulate_branch_creation(bug_issue, bug_template)
    expected_branch_name = "bugfix/1-memory-leak-in-template-parser"
    assert bugfix_branch["name"] == expected_branch_name
    assert bugfix_branch["is_valid"] == True
    print("  ✓ Bugfix branch created")
    
    # Create hotfix PR (critical bug)
    hotfix_pr_body = """## Changes Summary
This PR fixes the critical memory leak in the template parser by:
- Adding proper cleanup of YAML parser objects
- Implementing explicit garbage collection after large file parsing
- Adding memory usage monitoring and limits

## Related Issues
Fixes #1

## Testing Checklist
- [x] Memory leak reproduction test passes
- [x] Unit tests for parser cleanup
- [x] Integration tests with large files
- [x] Performance regression tests
- [ ] Production deployment test

## Breaking Changes
None - internal implementation change only.

## Deployment Notes
This is a critical hotfix and should be deployed immediately.
Monitor memory usage after deployment.
"""
    
    hotfix_pr = tester.simulate_pr_creation(bugfix_branch, hotfix_pr_body)
    print("  ✓ Hotfix PR created")
    
    # Update bug to resolved
    resolved_bug = tester.simulate_issue_update(1, {
        "state": "closed",
        "labels": ["bug", "critical", "memory-leak", "performance", "resolved"]
    })
    
    resolved_template = tester.simulate_template_parsing(resolved_bug)
    resolved_dashboard = tester.simulate_dashboard_mapping(resolved_template, resolved_bug)
    assert resolved_dashboard["status"] == "done"
    print("  ✓ Bug marked as resolved")
    
    print("  ✓ Bug fix workflow test passed")

def test_multi_issue_dashboard_sync():
    """Test dashboard synchronization with multiple issues"""
    print("Testing multi-issue dashboard synchronization...")
    
    tester = EndToEndWorkflowTester()
    
    # Create multiple issues of different types
    issues_data = [
        {
            "title": "Add user dashboard",
            "body": """---
template_type: feature
priority: medium
estimated_time: 8
acceptance_criteria:
  - "[x] Design dashboard layout"
  - "[ ] Implement dashboard components"
  - "[ ] Add data visualization"
---""",
            "labels": ["feature", "ui", "dashboard"]
        },
        {
            "title": "Fix login button styling",
            "body": """---
template_type: bug
priority: low
reproduction_steps:
  - "Navigate to login page"
  - "Observe button styling"
expected_behavior: Button should match design system
actual_behavior: Button has incorrect colors and spacing
---""",
            "labels": ["bug", "ui", "styling"]
        },
        {
            "title": "Update dependencies",
            "body": """---
template_type: task
priority: medium
checklist:
  - "[x] Audit current dependencies"
  - "[ ] Update to latest versions"
  - "[ ] Test for breaking changes"
  - "[ ] Update documentation"
---""",
            "labels": ["task", "maintenance", "dependencies"]
        }
    ]
    
    # Create all issues
    created_issues = []
    for issue_data in issues_data:
        github_issue = tester.simulate_github_issue_creation(issue_data)
        template_data = tester.simulate_template_parsing(github_issue)
        dashboard_data = tester.simulate_dashboard_mapping(template_data, github_issue)
        created_issues.append((github_issue, template_data, dashboard_data))
    
    assert len(created_issues) == 3
    print("  ✓ Multiple issues created and mapped")
    
    # Verify different categories
    categories = [dashboard["category"] for _, _, dashboard in created_issues]
    assert "feature" in categories
    assert "bug" in categories
    assert "task" in categories
    print("  ✓ Different issue categories detected")
    
    # Update one issue and verify sync
    tester.simulate_issue_update(1, {"assignees": ["developer1"]})
    updated_issue = tester.github_state["issues"][1]
    updated_template = tester.simulate_template_parsing(updated_issue)
    updated_dashboard = tester.simulate_dashboard_mapping(updated_template, updated_issue)
    
    # Verify sync
    assert tester.verify_dashboard_sync(1)
    print("  ✓ Dashboard synchronization verified")
    
    # Get dashboard statistics
    all_dashboard_data = [tester.dashboard_state[i] for i in range(1, 4)]
    
    # Verify statistics
    feature_count = sum(1 for item in all_dashboard_data if item["category"] == "feature")
    bug_count = sum(1 for item in all_dashboard_data if item["category"] == "bug")
    task_count = sum(1 for item in all_dashboard_data if item["category"] == "task")
    
    assert feature_count == 1
    assert bug_count == 1
    assert task_count == 1
    print("  ✓ Dashboard statistics correct")
    
    print("  ✓ Multi-issue dashboard sync test passed")

def test_branch_naming_enforcement():
    """Test branch naming convention enforcement"""
    print("Testing branch naming convention enforcement...")
    
    tester = EndToEndWorkflowTester()
    
    # Create issue
    issue_data = {
        "title": "Implement API rate limiting",
        "body": """---
template_type: feature
priority: high
---""",
        "labels": ["feature", "api"]
    }
    
    github_issue = tester.simulate_github_issue_creation(issue_data)
    template_data = tester.simulate_template_parsing(github_issue)
    
    # Test valid branch names
    valid_branches = [
        "feature/1-implement-api-rate-limiting",
        "feature/1-api-rate-limiting",
        "feat/1-rate-limiting"
    ]
    
    for branch_name in valid_branches:
        # Simulate manual branch creation with custom name
        branch_info = branch_naming_service.parse_branch_name(branch_name)
        is_valid, errors = branch_naming_service.validate_branch_name(branch_name)
        
        assert is_valid, f"Branch '{branch_name}' should be valid, errors: {errors}"
        assert branch_info.issue_number == 1
        print(f"  ✓ Valid branch name: {branch_name}")
    
    # Test invalid branch names
    invalid_branches = [
        "feature/1-a",  # Too short
        "feature/1-",   # Empty description
        "feature/abc-test",  # Non-numeric issue
        "random-branch-name",  # No pattern match
        "feature/1-invalid@chars"  # Invalid characters
    ]
    
    for branch_name in invalid_branches:
        is_valid, errors = branch_naming_service.validate_branch_name(branch_name)
        assert not is_valid, f"Branch '{branch_name}' should be invalid"
        print(f"  ✓ Invalid branch name rejected: {branch_name}")
    
    # Test suggested branch name
    suggested = branch_naming_service.suggest_branch_name(
        github_issue["number"],
        github_issue["title"],
        BranchType.FEATURE
    )
    
    is_valid, errors = branch_naming_service.validate_branch_name(suggested)
    assert is_valid, f"Suggested branch name should be valid: {suggested}"
    print(f"  ✓ Suggested branch name is valid: {suggested}")
    
    print("  ✓ Branch naming enforcement test passed")

def test_real_time_updates_simulation():
    """Test real-time updates simulation"""
    print("Testing real-time updates simulation...")
    
    tester = EndToEndWorkflowTester()
    
    # Create initial issue
    issue_data = {
        "title": "Implement real-time notifications",
        "body": """---
template_type: feature
priority: high
acceptance_criteria:
  - "[ ] WebSocket connection established"
  - "[ ] Real-time message handling"
  - "[ ] UI updates on notifications"
  - "[ ] Error handling and reconnection"
---""",
        "labels": ["feature", "real-time", "websockets"]
    }
    
    github_issue = tester.simulate_github_issue_creation(issue_data)
    initial_template = tester.simulate_template_parsing(github_issue)
    initial_dashboard = tester.simulate_dashboard_mapping(initial_template, github_issue)
    
    initial_progress = initial_dashboard["progress"]
    print(f"  ✓ Initial progress: {initial_progress}%")
    
    # Simulate progress updates
    progress_updates = [
        ("[ ] WebSocket connection established", "[x] WebSocket connection established"),
        ("[ ] Real-time message handling", "[x] Real-time message handling"),
        ("[ ] UI updates on notifications", "[x] UI updates on notifications")
    ]
    
    current_body = github_issue["body"]
    for old_criterion, new_criterion in progress_updates:
        # Update acceptance criteria
        current_body = current_body.replace(old_criterion, new_criterion)
        
        updated_issue = tester.simulate_issue_update(1, {"body": current_body})
        updated_template = tester.simulate_template_parsing(updated_issue)
        updated_dashboard = tester.simulate_dashboard_mapping(updated_template, updated_issue)
        
        new_progress = updated_dashboard["progress"]
        assert new_progress > initial_progress, "Progress should increase"
        
        print(f"  ✓ Progress updated: {new_progress}%")
        initial_progress = new_progress
    
    # Final completion
    final_body = current_body.replace(
        "[ ] Error handling and reconnection",
        "[x] Error handling and reconnection"
    )
    
    completed_issue = tester.simulate_issue_update(1, {
        "body": final_body,
        "state": "closed"
    })
    
    completed_template = tester.simulate_template_parsing(completed_issue)
    completed_dashboard = tester.simulate_dashboard_mapping(completed_template, completed_issue)
    
    assert completed_dashboard["status"] == "done"
    assert completed_dashboard["acceptance_criteria_completed"] == 4
    print("  ✓ Issue completed with all criteria met")
    
    print("  ✓ Real-time updates simulation test passed")

def main():
    """Run all end-to-end workflow tests"""
    print("Running comprehensive end-to-end workflow tests...\n")
    
    try:
        test_complete_feature_workflow()
        print()
        test_bug_fix_workflow()
        print()
        test_multi_issue_dashboard_sync()
        print()
        test_branch_naming_enforcement()
        print()
        test_real_time_updates_simulation()
        
        print("\n🎉 All end-to-end workflow tests passed!")
        print("\nComplete GitHub template system workflow is ready for production!")
        return 0
    except Exception as e:
        print(f"\n❌ End-to-end workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())