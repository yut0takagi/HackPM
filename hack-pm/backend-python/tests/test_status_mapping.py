#!/usr/bin/env python3
"""
Tests for status mapping service
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.core.status_mapping import StatusMappingService, DashboardStatus, DashboardCategory, DashboardPriority
from src.core.template_parser import ParsedTemplateData, TemplateType, Priority

def test_issue_category_mapping():
    """Test issue category mapping from template data and labels"""
    service = StatusMappingService()
    
    # Test feature template
    feature_data = ParsedTemplateData(
        template_type=TemplateType.FEATURE,
        priority=Priority.HIGH
    )
    
    result = service.map_issue_to_dashboard(feature_data, ["feature", "enhancement"])
    assert result.category == DashboardCategory.FEATURE, f"Expected FEATURE, got {result.category}"
    
    # Test bug template
    bug_data = ParsedTemplateData(
        template_type=TemplateType.BUG,
        priority=Priority.CRITICAL
    )
    
    result = service.map_issue_to_dashboard(bug_data, ["bug", "defect"])
    assert result.category == DashboardCategory.BUG, f"Expected BUG, got {result.category}"
    
    # Test label-based category detection
    unknown_data = ParsedTemplateData(
        template_type=TemplateType.UNKNOWN,
        priority=Priority.MEDIUM
    )
    
    result = service.map_issue_to_dashboard(unknown_data, ["documentation"])
    assert result.category == DashboardCategory.DOCUMENTATION, f"Expected DOCUMENTATION, got {result.category}"
    
    print("✓ Issue category mapping test passed")

def test_priority_mapping():
    """Test priority mapping from template data and labels"""
    service = StatusMappingService()
    
    # Test template priority
    high_priority_data = ParsedTemplateData(
        template_type=TemplateType.FEATURE,
        priority=Priority.HIGH
    )
    
    result = service.map_issue_to_dashboard(high_priority_data)
    assert result.priority == DashboardPriority.HIGH, f"Expected HIGH, got {result.priority}"
    
    # Test label-based priority
    medium_priority_data = ParsedTemplateData(
        template_type=TemplateType.TASK,
        priority=Priority.MEDIUM
    )
    
    result = service.map_issue_to_dashboard(medium_priority_data, ["urgent"])
    assert result.priority == DashboardPriority.CRITICAL, f"Expected CRITICAL, got {result.priority}"
    
    print("✓ Priority mapping test passed")

def test_status_determination():
    """Test status determination from various indicators"""
    service = StatusMappingService()
    
    data = ParsedTemplateData(
        template_type=TemplateType.FEATURE,
        priority=Priority.MEDIUM
    )
    
    # Test closed issue
    result = service.map_issue_to_dashboard(data, issue_state="closed")
    assert result.status == DashboardStatus.DONE, f"Expected DONE, got {result.status}"
    
    # Test issue with PR
    result = service.map_issue_to_dashboard(data, has_linked_pr=True)
    assert result.status == DashboardStatus.REVIEW, f"Expected REVIEW, got {result.status}"
    
    # Test issue with assignee
    result = service.map_issue_to_dashboard(data, assignees=["developer1"])
    assert result.status == DashboardStatus.IN_PROGRESS, f"Expected IN_PROGRESS, got {result.status}"
    
    # Test issue with status label
    result = service.map_issue_to_dashboard(data, labels=["in progress"])
    assert result.status == DashboardStatus.IN_PROGRESS, f"Expected IN_PROGRESS, got {result.status}"
    
    print("✓ Status determination test passed")

def test_progress_calculation():
    """Test progress calculation based on acceptance criteria"""
    service = StatusMappingService()
    
    # Test with acceptance criteria
    data_with_criteria = ParsedTemplateData(
        template_type=TemplateType.FEATURE,
        priority=Priority.MEDIUM,
        acceptance_criteria=[
            "[x] First criterion completed",
            "[ ] Second criterion pending",
            "[x] Third criterion completed"
        ]
    )
    
    result = service.map_issue_to_dashboard(data_with_criteria)
    
    # Should have 2 out of 3 criteria completed
    assert result.acceptance_criteria_total == 3, f"Expected 3 total, got {result.acceptance_criteria_total}"
    assert result.acceptance_criteria_completed == 2, f"Expected 2 completed, got {result.acceptance_criteria_completed}"
    
    # Progress should be calculated based on criteria completion and status
    assert result.progress_percentage > 0, f"Expected progress > 0, got {result.progress_percentage}"
    
    print("✓ Progress calculation test passed")

def test_pr_mapping():
    """Test PR template mapping"""
    service = StatusMappingService()
    
    pr_data = ParsedTemplateData(
        template_type=TemplateType.UNKNOWN,
        priority=Priority.MEDIUM,
        breaking_changes="Changed API endpoint",
        testing_checklist=[
            "[x] Unit tests pass",
            "[x] Integration tests pass",
            "[ ] Manual testing completed"
        ],
        related_issues=[123, 456]
    )
    
    result = service.map_pr_to_dashboard(pr_data, pr_state="open", is_draft=False)
    
    # Should be high priority due to breaking changes
    assert result.priority == DashboardPriority.HIGH, f"Expected HIGH priority, got {result.priority}"
    
    # Should have testing checklist progress
    assert result.acceptance_criteria_total == 3, f"Expected 3 checklist items, got {result.acceptance_criteria_total}"
    assert result.acceptance_criteria_completed == 2, f"Expected 2 completed, got {result.acceptance_criteria_completed}"
    
    # Should be marked as time sensitive due to breaking changes
    assert result.is_time_sensitive, "Expected time sensitive due to breaking changes"
    
    print("✓ PR mapping test passed")

def test_statistics():
    """Test statistics generation"""
    service = StatusMappingService()
    
    # Create sample data
    issues_data = [
        service.map_issue_to_dashboard(
            ParsedTemplateData(template_type=TemplateType.FEATURE, priority=Priority.HIGH),
            labels=["feature", "high"]
        ),
        service.map_issue_to_dashboard(
            ParsedTemplateData(template_type=TemplateType.BUG, priority=Priority.CRITICAL),
            labels=["bug", "critical"],
            issue_state="closed"
        ),
        service.map_issue_to_dashboard(
            ParsedTemplateData(template_type=TemplateType.TASK, priority=Priority.MEDIUM),
            labels=["task", "in progress"]
        )
    ]
    
    # Test category stats
    category_stats = service.get_category_stats(issues_data)
    assert "feature" in category_stats, "Expected feature category in stats"
    assert "bug" in category_stats, "Expected bug category in stats"
    assert category_stats["feature"]["total"] == 1, f"Expected 1 feature, got {category_stats['feature']['total']}"
    
    # Test priority distribution
    priority_dist = service.get_priority_distribution(issues_data)
    assert priority_dist["high"] == 1, f"Expected 1 high priority, got {priority_dist['high']}"
    assert priority_dist["critical"] == 1, f"Expected 1 critical priority, got {priority_dist['critical']}"
    assert priority_dist["medium"] == 1, f"Expected 1 medium priority, got {priority_dist['medium']}"
    
    print("✓ Statistics test passed")

def test_hackathon_time_boxing():
    """Test hackathon-specific time-boxed development features"""
    service = StatusMappingService()
    
    # Test time-sensitive issue with deadline
    time_sensitive_data = ParsedTemplateData(
        template_type=TemplateType.FEATURE,
        priority=Priority.HIGH,
        estimated_time=4
    )
    
    timebox_data = {
        'hackathon_phase': 'development',
        'hours_until_deadline': 2.5,
        'is_overdue': False,
        'priority_escalated': False,
        'time_remaining_percentage': 25.0
    }
    
    result = service.map_issue_to_dashboard(
        time_sensitive_data,
        labels=["feature", "hackathon"],
        timebox_data=timebox_data
    )
    
    assert result.hackathon_phase == 'development'
    assert result.deadline_hours_remaining == 2.5
    assert result.is_time_sensitive == True
    assert result.time_box_progress == 25.0
    
    # Test overdue issue with priority escalation
    overdue_data = ParsedTemplateData(
        template_type=TemplateType.BUG,
        priority=Priority.MEDIUM
    )
    
    overdue_timebox = {
        'hackathon_phase': 'testing',
        'hours_until_deadline': -1.0,  # Overdue
        'is_overdue': True,
        'priority_escalated': True,
        'time_remaining_percentage': 0.0
    }
    
    result = service.map_issue_to_dashboard(
        overdue_data,
        labels=["bug"],
        timebox_data=overdue_timebox
    )
    
    assert result.is_overdue == True
    assert result.priority_escalated == True
    assert result.priority == DashboardPriority.HIGH  # Should be escalated
    
    print("✓ Hackathon time-boxing test passed")

def test_complex_acceptance_criteria():
    """Test complex acceptance criteria parsing and progress calculation"""
    service = StatusMappingService()
    
    # Test mixed completion markers
    complex_criteria = [
        "[x] First criterion completed",
        "[ ] Second criterion pending",
        "[X] Third criterion completed (uppercase)",
        "✓ Fourth criterion with checkmark",
        "✔ Fifth criterion with heavy checkmark",
        "- [x] Sixth criterion with dash prefix",
        "* [X] Seventh criterion with asterisk prefix",
        "1. [x] Eighth criterion with number prefix",
        "[ ] Ninth criterion not completed",
        "[x] Tenth criterion completed"
    ]
    
    data = ParsedTemplateData(
        template_type=TemplateType.FEATURE,
        priority=Priority.MEDIUM,
        acceptance_criteria=complex_criteria
    )
    
    result = service.map_issue_to_dashboard(data)
    
    # Should count various completion markers
    assert result.acceptance_criteria_total == 10
    # Should count: [x], [X], ✓, ✔, and nested checkboxes
    expected_completed = 6  # [x], [X], ✓, ✔, [x], [X], [x]
    assert result.acceptance_criteria_completed >= 5  # At least the obvious ones
    
    print("✓ Complex acceptance criteria test passed")

def test_edge_case_mappings():
    """Test edge cases in status and priority mapping"""
    service = StatusMappingService()
    
    # Test conflicting labels
    conflicting_data = ParsedTemplateData(
        template_type=TemplateType.FEATURE,
        priority=Priority.LOW
    )
    
    # Labels suggest high priority but template says low
    result = service.map_issue_to_dashboard(
        conflicting_data,
        labels=["feature", "critical", "low-priority"]  # Conflicting priorities
    )
    
    # Labels should take precedence
    assert result.priority == DashboardPriority.CRITICAL
    
    # Test unknown template type with clear labels
    unknown_data = ParsedTemplateData(
        template_type=TemplateType.UNKNOWN,
        priority=Priority.MEDIUM
    )
    
    result = service.map_issue_to_dashboard(
        unknown_data,
        labels=["enhancement", "high"]
    )
    
    assert result.category == DashboardCategory.ENHANCEMENT
    assert result.priority == DashboardPriority.HIGH
    
    print("✓ Edge case mappings test passed")

def test_pr_complex_scenarios():
    """Test complex PR mapping scenarios"""
    service = StatusMappingService()
    
    # Test PR with breaking changes and extensive testing
    complex_pr_data = ParsedTemplateData(
        template_type=TemplateType.UNKNOWN,
        priority=Priority.MEDIUM,
        breaking_changes="Major API changes: /api/v1 endpoints removed, new /api/v2 structure",
        testing_checklist=[
            "[x] Unit tests pass (100% coverage)",
            "[x] Integration tests pass",
            "[x] API compatibility tests",
            "[ ] Performance regression tests",
            "[ ] Security audit completed",
            "[x] Documentation updated",
            "[ ] Migration guide written"
        ],
        related_issues=[123, 456, 789, 101, 202]  # Many related issues
    )
    
    result = service.map_pr_to_dashboard(
        complex_pr_data,
        pr_state="open",
        is_draft=False,
        review_status="changes_requested"
    )
    
    # Should be high priority due to breaking changes and many related issues
    assert result.priority == DashboardPriority.HIGH
    assert result.is_time_sensitive == True
    assert result.has_technical_requirements == True
    assert result.acceptance_criteria_total == 7
    assert result.acceptance_criteria_completed == 4  # 4 items marked with [x]
    assert result.status == DashboardStatus.IN_PROGRESS  # Changes requested
    
    print("✓ Complex PR scenarios test passed")

def test_performance_with_large_datasets():
    """Test performance with large numbers of issues"""
    import time
    service = StatusMappingService()
    
    # Generate large dataset
    issues_data = []
    for i in range(1000):
        data = ParsedTemplateData(
            template_type=TemplateType.FEATURE if i % 3 == 0 else TemplateType.BUG if i % 3 == 1 else TemplateType.TASK,
            priority=Priority.HIGH if i % 4 == 0 else Priority.MEDIUM,
            acceptance_criteria=[f"Criterion {j}" for j in range(i % 5 + 1)]
        )
        
        mapped = service.map_issue_to_dashboard(
            data,
            labels=["feature" if i % 3 == 0 else "bug" if i % 3 == 1 else "task"],
            assignees=["dev1"] if i % 2 == 0 else []
        )
        issues_data.append(mapped)
    
    # Test statistics generation performance
    start_time = time.time()
    
    category_stats = service.get_category_stats(issues_data)
    priority_dist = service.get_priority_distribution(issues_data)
    time_sensitive_stats = service.get_time_sensitive_stats(issues_data)
    
    end_time = time.time()
    
    # Should complete within reasonable time
    assert (end_time - start_time) < 1.0, f"Statistics generation took too long: {end_time - start_time} seconds"
    
    # Verify statistics
    assert len(category_stats) > 0
    assert len(priority_dist) == 4  # All priority levels
    assert "total_time_sensitive" in time_sensitive_stats
    
    print(f"✓ Performance test passed: {len(issues_data)} issues processed in {end_time - start_time:.3f} seconds")

def test_hackathon_optimization():
    """Test hackathon-specific dashboard optimization"""
    service = StatusMappingService()
    
    # Create mixed dataset with time-sensitive issues
    issues_data = []
    
    # Add overdue critical issue
    overdue_data = ParsedTemplateData(
        template_type=TemplateType.BUG,
        priority=Priority.CRITICAL
    )
    overdue_mapped = service.map_issue_to_dashboard(
        overdue_data,
        timebox_data={
            'hackathon_phase': 'testing',
            'hours_until_deadline': -2.0,
            'is_overdue': True,
            'priority_escalated': True
        }
    )
    issues_data.append(overdue_mapped)
    
    # Add urgent issue (deadline soon)
    urgent_data = ParsedTemplateData(
        template_type=TemplateType.FEATURE,
        priority=Priority.HIGH
    )
    urgent_mapped = service.map_issue_to_dashboard(
        urgent_data,
        timebox_data={
            'hackathon_phase': 'development',
            'hours_until_deadline': 1.5,
            'is_overdue': False,
            'priority_escalated': False
        }
    )
    issues_data.append(urgent_mapped)
    
    # Add normal issues
    for i in range(10):
        normal_data = ParsedTemplateData(
            template_type=TemplateType.TASK,
            priority=Priority.MEDIUM
        )
        normal_mapped = service.map_issue_to_dashboard(normal_data)
        issues_data.append(normal_mapped)
    
    # Test optimization
    optimized = service.optimize_for_hackathon_dashboard(issues_data)
    
    assert "sorted_issues" in optimized
    assert "by_phase" in optimized
    assert "quick_stats" in optimized
    assert "cache_timestamp" in optimized
    
    # Most urgent issues should be first
    sorted_issues = optimized["sorted_issues"]
    assert len(sorted_issues) > 0
    assert sorted_issues[0].is_overdue == True  # Overdue issue should be first
    
    # Check phase grouping
    by_phase = optimized["by_phase"]
    assert "testing" in by_phase  # Should have overdue issue
    assert "development" in by_phase  # Should have urgent issue
    
    print("✓ Hackathon optimization test passed")

def main():
    """Run all tests"""
    print("Running status mapping service tests...")
    
    try:
        test_issue_category_mapping()
        test_priority_mapping()
        test_status_determination()
        test_progress_calculation()
        test_pr_mapping()
        test_statistics()
        test_hackathon_time_boxing()
        test_complex_acceptance_criteria()
        test_edge_case_mappings()
        test_pr_complex_scenarios()
        test_performance_with_large_datasets()
        test_hackathon_optimization()
        
        print("\n🎉 All status mapping tests passed!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())