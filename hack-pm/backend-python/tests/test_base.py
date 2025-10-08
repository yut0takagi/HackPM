#!/usr/bin/env python3
"""
Base test utilities and common functionality for GitHub template system tests
"""
import sys
import os
import time
import traceback
from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod

sys.path.append(os.path.dirname(__file__))

class TestResult:
    """Represents the result of a test execution"""
    
    def __init__(self, name: str, success: bool, duration: float, error: Optional[str] = None):
        self.name = name
        self.success = success
        self.duration = duration
        self.error = error
        self.timestamp = time.time()

class BaseTestSuite(ABC):
    """Base class for test suites with common functionality"""
    
    def __init__(self, name: str):
        self.name = name
        self.results: List[TestResult] = []
        self.setup_completed = False
        
    def setup(self):
        """Setup method to be overridden by subclasses"""
        self.setup_completed = True
        
    def teardown(self):
        """Teardown method to be overridden by subclasses"""
        pass
        
    def run_test(self, test_method: Callable, test_name: str) -> TestResult:
        """Run a single test method and return result"""
        if not self.setup_completed:
            self.setup()
            
        start_time = time.time()
        
        try:
            test_method()
            duration = time.time() - start_time
            result = TestResult(test_name, True, duration)
            print(f"  ✓ {test_name} ({duration:.3f}s)")
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"{type(e).__name__}: {str(e)}"
            result = TestResult(test_name, False, duration, error_msg)
            print(f"  ❌ {test_name} - {error_msg}")
            
        self.results.append(result)
        return result
        
    @abstractmethod
    def get_test_methods(self) -> List[tuple]:
        """Return list of (method, name) tuples for tests to run"""
        pass
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests in the suite"""
        print(f"Running {self.name}...")
        
        start_time = time.time()
        test_methods = self.get_test_methods()
        
        for test_method, test_name in test_methods:
            self.run_test(test_method, test_name)
            
        total_time = time.time() - start_time
        passed = sum(1 for r in self.results if r.success)
        failed = len(self.results) - passed
        
        print(f"\n{self.name} Summary:")
        print(f"  Tests: {len(self.results)}, Passed: {passed}, Failed: {failed}")
        print(f"  Total time: {total_time:.3f}s")
        
        if failed == 0:
            print(f"🎉 All {self.name.lower()} passed!")
        else:
            print(f"❌ {failed} test(s) failed in {self.name.lower()}")
            
        self.teardown()
        
        return {
            "suite_name": self.name,
            "total_tests": len(self.results),
            "passed_tests": passed,
            "failed_tests": failed,
            "total_time": total_time,
            "results": self.results,
            "success": failed == 0
        }

class MockDataGenerator:
    """Utility class for generating mock test data"""
    
    @staticmethod
    def create_yaml_template(template_type: str = "feature", **kwargs) -> str:
        """Create a YAML template with specified parameters"""
        defaults = {
            "priority": "medium",
            "estimated_time": 4,
            "user_story": "As a user, I want functionality, so that I can achieve my goals",
            "acceptance_criteria": [
                "[ ] First criterion",
                "[ ] Second criterion"
            ],
            "technical_requirements": [
                "Implement core functionality",
                "Add proper error handling"
            ]
        }
        
        # Merge defaults with provided kwargs
        template_data = {**defaults, **kwargs}
        template_data["template_type"] = template_type
        
        yaml_content = "---\n"
        for key, value in template_data.items():
            if isinstance(value, list):
                yaml_content += f"{key}:\n"
                for item in value:
                    yaml_content += f"  - \"{item}\"\n"
            else:
                yaml_content += f"{key}: {value}\n"
        yaml_content += "---\n\n## Description\nGenerated test template."
        
        return yaml_content
    
    @staticmethod
    def create_markdown_template(template_type: str = "feature", **kwargs) -> str:
        """Create a markdown template with specified parameters"""
        if template_type == "feature":
            return """# Feature Request

## User Story
As a user, I want to see functionality, so that I can be productive.

## Acceptance Criteria
1. Feature should work correctly
2. Feature should be user-friendly
3. Feature should be performant

## Technical Requirements
- Implement with modern frameworks
- Add comprehensive testing
- Ensure security compliance
"""
        elif template_type == "bug":
            return """# Bug Report

## Reproduction Steps
1. Navigate to the page
2. Perform the action
3. Observe the error

## Expected Behavior
Should work correctly

## Actual Behavior
Throws an error

## Environment
- OS: Test OS
- Browser: Test Browser
"""
        else:
            return "# Generic Template\n\nThis is a generic test template."
    
    @staticmethod
    def create_pr_template(**kwargs) -> str:
        """Create a PR template with specified parameters"""
        defaults = {
            "summary": "This PR implements new functionality",
            "related_issues": [123, 456],
            "breaking_changes": None,
            "testing_checklist": [
                "[x] Unit tests pass",
                "[ ] Integration tests pass",
                "[ ] Manual testing completed"
            ]
        }
        
        template_data = {**defaults, **kwargs}
        
        pr_content = f"""## Changes Summary
{template_data['summary']}

## Related Issues
"""
        for issue in template_data['related_issues']:
            pr_content += f"Fixes #{issue}\n"
            
        pr_content += "\n## Testing Checklist\n"
        for item in template_data['testing_checklist']:
            pr_content += f"- {item}\n"
            
        if template_data['breaking_changes']:
            pr_content += f"\n## Breaking Changes\n{template_data['breaking_changes']}\n"
            
        return pr_content

class PerformanceBenchmark:
    """Utility class for performance benchmarking"""
    
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
        self.measurements = []
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.measurements.append(duration)
            
    def measure_operation(self, operation: Callable, iterations: int = 1) -> Dict[str, float]:
        """Measure the performance of an operation"""
        times = []
        
        for _ in range(iterations):
            start = time.time()
            operation()
            end = time.time()
            times.append(end - start)
            
        return {
            "total_time": sum(times),
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "iterations": iterations
        }
        
    def get_stats(self) -> Dict[str, float]:
        """Get statistics for all measurements"""
        if not self.measurements:
            return {}
            
        return {
            "total_measurements": len(self.measurements),
            "total_time": sum(self.measurements),
            "average_time": sum(self.measurements) / len(self.measurements),
            "min_time": min(self.measurements),
            "max_time": max(self.measurements)
        }

class TestAssertions:
    """Enhanced assertion utilities for tests"""
    
    @staticmethod
    def assert_template_data_valid(data, expected_type=None, expected_priority=None):
        """Assert that template data is valid"""
        assert data is not None, "Template data should not be None"
        assert hasattr(data, 'template_type'), "Template data should have template_type"
        assert hasattr(data, 'priority'), "Template data should have priority"
        
        if expected_type:
            assert data.template_type == expected_type, f"Expected {expected_type}, got {data.template_type}"
            
        if expected_priority:
            assert data.priority == expected_priority, f"Expected {expected_priority}, got {data.priority}"
            
    @staticmethod
    def assert_dashboard_data_valid(data, expected_category=None, expected_status=None):
        """Assert that dashboard data is valid"""
        assert data is not None, "Dashboard data should not be None"
        assert hasattr(data, 'category'), "Dashboard data should have category"
        assert hasattr(data, 'status'), "Dashboard data should have status"
        assert hasattr(data, 'priority'), "Dashboard data should have priority"
        
        if expected_category:
            assert data.category == expected_category, f"Expected {expected_category}, got {data.category}"
            
        if expected_status:
            assert data.status == expected_status, f"Expected {expected_status}, got {data.status}"
            
    @staticmethod
    def assert_branch_info_valid(info, expected_type=None, expected_issue=None):
        """Assert that branch info is valid"""
        assert info is not None, "Branch info should not be None"
        assert hasattr(info, 'branch_type'), "Branch info should have branch_type"
        assert hasattr(info, 'is_valid'), "Branch info should have is_valid"
        
        if expected_type:
            assert info.branch_type == expected_type, f"Expected {expected_type}, got {info.branch_type}"
            
        if expected_issue:
            assert info.issue_number == expected_issue, f"Expected issue {expected_issue}, got {info.issue_number}"
            
    @staticmethod
    def assert_performance_acceptable(duration: float, max_duration: float, operation_name: str):
        """Assert that operation performance is acceptable"""
        assert duration <= max_duration, f"{operation_name} took {duration:.3f}s, expected <= {max_duration:.3f}s"
        
    @staticmethod
    def assert_list_contains_items(items: List, expected_items: List, partial_match: bool = False):
        """Assert that list contains expected items"""
        if partial_match:
            for expected in expected_items:
                found = any(expected in str(item) for item in items)
                assert found, f"Expected to find '{expected}' in {items}"
        else:
            for expected in expected_items:
                assert expected in items, f"Expected '{expected}' in {items}"

def run_test_suite(suite_class, *args, **kwargs) -> Dict[str, Any]:
    """Utility function to run a test suite"""
    suite = suite_class(*args, **kwargs)
    return suite.run_all_tests()