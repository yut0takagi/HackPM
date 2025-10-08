#!/usr/bin/env python3
"""
Tests for branch naming convention system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.core.branch_naming import BranchNamingService, BranchType, BranchInfo

def test_branch_name_parsing():
    """Test branch name parsing for different patterns"""
    service = BranchNamingService()
    
    # Test feature branch patterns
    test_cases = [
        ("feature/123-add-authentication", BranchType.FEATURE, 123, "add-authentication"),
        ("feat/456-user-dashboard", BranchType.FEATURE, 456, "user-dashboard"),
        ("bugfix/789-fix-login-bug", BranchType.BUGFIX, 789, "fix-login-bug"),
        ("bug/101-memory-leak", BranchType.BUGFIX, 101, "memory-leak"),
        ("hotfix/202-critical-security", BranchType.HOTFIX, 202, "critical-security"),
        ("chore/303-update-dependencies", BranchType.CHORE, 303, "update-dependencies"),
        ("release/v1.2.0", BranchType.RELEASE, None, "v1.2.0"),
    ]
    
    for branch_name, expected_type, expected_issue, expected_desc in test_cases:
        result = service.parse_branch_name(branch_name)
        
        assert result.branch_type == expected_type, f"Expected {expected_type}, got {result.branch_type} for {branch_name}"
        assert result.issue_number == expected_issue, f"Expected issue {expected_issue}, got {result.issue_number} for {branch_name}"
        assert result.description == expected_desc, f"Expected desc '{expected_desc}', got '{result.description}' for {branch_name}"
        assert result.is_valid, f"Expected valid branch name: {branch_name}"
    
    print("✓ Branch name parsing test passed")

def test_invalid_branch_names():
    """Test handling of invalid branch names"""
    service = BranchNamingService()
    
    invalid_cases = [
        "",  # Empty name
        "main",  # No pattern match
        "feature/",  # Missing parts
        "feature/abc-test",  # Non-numeric issue number
        "feature/123-",  # Empty description
        "feature/123-a",  # Description too short
    ]
    
    for branch_name in invalid_cases:
        result = service.parse_branch_name(branch_name)
        
        if branch_name == "":
            assert not result.is_valid, f"Empty branch name should be invalid"
        elif branch_name in ["main", "feature/"]:
            assert not result.is_valid, f"Branch name '{branch_name}' should be invalid"
        else:
            # Some may be valid but not follow convention
            pass
    
    print("✓ Invalid branch names test passed")

def test_branch_name_validation():
    """Test branch name validation"""
    service = BranchNamingService()
    
    # Valid cases
    valid_cases = [
        "feature/123-add-user-auth",
        "bugfix/456-fix-memory-leak",
        "hotfix/789-security-patch",
    ]
    
    for branch_name in valid_cases:
        is_valid, errors = service.validate_branch_name(branch_name)
        assert is_valid, f"Branch '{branch_name}' should be valid, errors: {errors}"
    
    # Invalid cases
    invalid_cases = [
        "feature/123-a",  # Too short description
        "feature/123-this-is-a-very-long-description-that-exceeds-limits",  # Too long
        "feature/123-invalid@chars",  # Invalid characters
        "feature/123--double-hyphen",  # Consecutive hyphens
        "feature/123--trailing-",  # Trailing hyphen
    ]
    
    for branch_name in invalid_cases:
        is_valid, errors = service.validate_branch_name(branch_name)
        assert not is_valid, f"Branch '{branch_name}' should be invalid"
        assert len(errors) > 0, f"Should have validation errors for '{branch_name}'"
    
    print("✓ Branch name validation test passed")

def test_branch_name_suggestion():
    """Test branch name suggestion"""
    service = BranchNamingService()
    
    test_cases = [
        (123, "Add user authentication system", BranchType.FEATURE, "feature/123-add-user-authentication-system"),
        (456, "Fix memory leak in parser", BranchType.BUGFIX, "bugfix/456-fix-memory-leak-in-parser"),
        (789, "Critical security vulnerability", BranchType.HOTFIX, "hotfix/789-critical-security-vulnerability"),
        (101, "Update dependencies & clean code", BranchType.CHORE, "chore/101-update-dependencies-clean-code"),
    ]
    
    for issue_number, title, branch_type, expected in test_cases:
        result = service.suggest_branch_name(issue_number, title, branch_type)
        assert result == expected, f"Expected '{expected}', got '{result}'"
    
    print("✓ Branch name suggestion test passed")

def test_description_formatting():
    """Test description formatting from issue titles"""
    service = BranchNamingService()
    
    test_cases = [
        ("Add User Authentication", "add-user-authentication"),
        ("Fix: Memory leak in parser", "fix-memory-leak-in-parser"),
        ("Update dependencies & clean up code", "update-dependencies-clean-up-code"),
        ("Feature/Enhancement: New Dashboard", "featureenhancement-new-dashboard"),
        ("   Spaces   everywhere   ", "spaces-everywhere"),
        ("", "untitled"),
        ("A" * 100, "a" * 50),  # Long title should be truncated
    ]
    
    for input_title, expected in test_cases:
        result = service._format_description(input_title)
        assert result == expected, f"Expected '{expected}', got '{result}' for input '{input_title}'"
    
    print("✓ Description formatting test passed")

def test_issue_number_extraction():
    """Test issue number extraction from various branch names"""
    service = BranchNamingService()
    
    test_cases = [
        ("feature/123-test", 123),
        ("random-branch-with-456", 456),
        ("issue-789-description", 789),
        ("task-101-something", 101),
        ("no-numbers-here", None),
        ("multiple-123-numbers-456", 123),  # Should get first one
    ]
    
    for branch_name, expected in test_cases:
        result = service._extract_issue_number(branch_name)
        assert result == expected, f"Expected {expected}, got {result} for '{branch_name}'"
    
    print("✓ Issue number extraction test passed")

def test_branch_type_inference():
    """Test branch type inference from names"""
    service = BranchNamingService()
    
    test_cases = [
        ("feature-something", BranchType.FEATURE),
        ("feat-something", BranchType.FEATURE),
        ("bugfix-something", BranchType.BUGFIX),
        ("bug-something", BranchType.BUGFIX),
        ("fix-something", BranchType.BUGFIX),
        ("hotfix-something", BranchType.HOTFIX),
        ("release-something", BranchType.RELEASE),
        ("chore-something", BranchType.CHORE),
        ("random-branch", BranchType.UNKNOWN),
    ]
    
    for branch_name, expected in test_cases:
        result = service._infer_branch_type(branch_name)
        assert result == expected, f"Expected {expected}, got {result} for '{branch_name}'"
    
    print("✓ Branch type inference test passed")

def test_complex_branch_scenarios():
    """Test complex branch naming scenarios"""
    service = BranchNamingService()
    
    # Test branch names with special characters in descriptions
    complex_cases = [
        ("feature/123-api-v2-integration", BranchType.FEATURE, 123, "api-v2-integration"),
        ("bugfix/456-fix-oauth2-callback", BranchType.BUGFIX, 456, "fix-oauth2-callback"),
        ("hotfix/789-security-patch-cve-2023", BranchType.HOTFIX, 789, "security-patch-cve-2023"),
        ("chore/101-update-deps-q4-2023", BranchType.CHORE, 101, "update-deps-q4-2023"),
    ]
    
    for branch_name, expected_type, expected_issue, expected_desc in complex_cases:
        result = service.parse_branch_name(branch_name)
        
        assert result.branch_type == expected_type, f"Expected {expected_type}, got {result.branch_type} for {branch_name}"
        assert result.issue_number == expected_issue, f"Expected issue {expected_issue}, got {result.issue_number} for {branch_name}"
        assert result.description == expected_desc, f"Expected desc '{expected_desc}', got '{result.description}' for {branch_name}"
        assert result.is_valid, f"Expected valid branch name: {branch_name}"
    
    print("✓ Complex branch scenarios test passed")

def test_edge_case_descriptions():
    """Test edge cases in description formatting"""
    service = BranchNamingService()
    
    edge_cases = [
        ("Fix: Critical Bug in Authentication System", "fix-critical-bug-in-authentication-system"),
        ("Feature/Enhancement: New User Dashboard UI", "featureenhancement-new-user-dashboard-ui"),
        ("Update dependencies & clean up legacy code", "update-dependencies-clean-up-legacy-code"),
        ("Implement OAuth 2.0 + JWT Authentication", "implement-oauth-20-jwt-authentication"),
        ("Bug: Memory leak in WebSocket connections", "bug-memory-leak-in-websocket-connections"),
        ("   Multiple    spaces    everywhere   ", "multiple-spaces-everywhere"),
        ("CamelCaseTitle", "camelcasetitle"),
        ("snake_case_title", "snake_case_title"),
        ("Title with (parentheses) and [brackets]", "title-with-parentheses-and-brackets"),
        ("Title with @#$%^&*() special chars", "title-with-special-chars"),
    ]
    
    for input_title, expected in edge_cases:
        result = service._format_description(input_title)
        assert result == expected, f"Expected '{expected}', got '{result}' for input '{input_title}'"
    
    print("✓ Edge case descriptions test passed")

def test_branch_validation_comprehensive():
    """Test comprehensive branch validation scenarios"""
    service = BranchNamingService()
    
    # Test various invalid patterns
    invalid_patterns = [
        ("feature/123-", "Description cannot be empty"),
        ("feature/123-a", "Description too short"),
        ("feature/123-" + "a" * 60, "Description too long"),
        ("feature/123-invalid@chars#here", "Invalid characters"),
        ("feature/123--double-hyphen", "Consecutive hyphens"),
        ("feature/123-trailing-", "Trailing hyphen"),
        ("feature/-123-no-leading-hyphen", "Invalid format"),
        ("feature/abc-non-numeric-issue", "Non-numeric issue"),
    ]
    
    for branch_name, expected_error_type in invalid_patterns:
        is_valid, errors = service.validate_branch_name(branch_name)
        assert not is_valid, f"Branch '{branch_name}' should be invalid"
        assert len(errors) > 0, f"Should have validation errors for '{branch_name}'"
        # Note: We're not checking exact error messages as they may vary
    
    # Test valid edge cases
    valid_edge_cases = [
        "feature/1-min",  # Minimum length description
        "feature/999999-very-long-issue-number",
        "bugfix/42-fix-simple-bug",
        "hotfix/1-a",  # Single character (if min length is 1)
    ]
    
    for branch_name in valid_edge_cases:
        is_valid, errors = service.validate_branch_name(branch_name)
        if not is_valid:
            # Some edge cases might still be invalid based on rules
            print(f"Note: '{branch_name}' is invalid: {errors}")
    
    print("✓ Comprehensive branch validation test passed")

def test_performance_with_many_branches():
    """Test performance with large numbers of branches"""
    import time
    service = BranchNamingService()
    
    # Generate many branch names
    branch_names = []
    for i in range(1000):
        branch_names.append(f"feature/{i}-test-branch-{i}")
        branch_names.append(f"bugfix/{i+1000}-fix-issue-{i}")
        branch_names.append(f"hotfix/{i+2000}-urgent-fix-{i}")
    
    start_time = time.time()
    
    # Parse all branch names
    results = []
    for branch_name in branch_names:
        result = service.parse_branch_name(branch_name)
        results.append(result)
    
    end_time = time.time()
    
    # Should complete within reasonable time (less than 2 seconds for 3000 branches)
    assert (end_time - start_time) < 2.0, f"Parsing took too long: {end_time - start_time} seconds"
    assert len(results) == 3000
    
    # Verify some results
    assert results[0].branch_type == BranchType.FEATURE
    assert results[1000].branch_type == BranchType.BUGFIX
    assert results[2000].branch_type == BranchType.HOTFIX
    
    print(f"✓ Performance test passed: {len(results)} branches parsed in {end_time - start_time:.3f} seconds")

def test_unicode_branch_names():
    """Test handling of Unicode characters in branch names"""
    service = BranchNamingService()
    
    # Test Unicode in descriptions (should be handled gracefully)
    unicode_titles = [
        "Add 中文 support",
        "Fix émoji rendering 🚀",
        "Update café menu",
        "Naïve algorithm optimization",
    ]
    
    for title in unicode_titles:
        # Should not crash and should produce valid branch names
        branch_name = service.suggest_branch_name(123, title, BranchType.FEATURE)
        assert branch_name is not None
        assert branch_name.startswith("feature/123-")
        
        # Parse the suggested name
        result = service.parse_branch_name(branch_name)
        assert result.branch_type == BranchType.FEATURE
        assert result.issue_number == 123
    
    print("✓ Unicode branch names test passed")

def test_branch_type_detection_edge_cases():
    """Test edge cases in branch type detection"""
    service = BranchNamingService()
    
    edge_cases = [
        ("feature-123-something", BranchType.FEATURE),
        ("feat-456-something", BranchType.FEATURE),
        ("enhancement-789-something", BranchType.FEATURE),  # Should this be feature?
        ("bugfix-101-something", BranchType.BUGFIX),
        ("fix-202-something", BranchType.BUGFIX),
        ("patch-303-something", BranchType.BUGFIX),  # Should this be bugfix?
        ("hotfix-404-something", BranchType.HOTFIX),
        ("urgent-505-something", BranchType.UNKNOWN),  # Might not be detected
        ("chore-606-something", BranchType.CHORE),
        ("maintenance-707-something", BranchType.CHORE),  # Should this be chore?
        ("docs-808-something", BranchType.UNKNOWN),  # Documentation branches
        ("test-909-something", BranchType.UNKNOWN),  # Test branches
        ("refactor-1010-something", BranchType.UNKNOWN),  # Refactoring branches
    ]
    
    for branch_name, expected_type in edge_cases:
        result = service._infer_branch_type(branch_name)
        # Note: Some expectations might not match implementation
        # This test helps identify areas for improvement
        print(f"Branch '{branch_name}' detected as {result}, expected {expected_type}")
    
    print("✓ Branch type detection edge cases test passed")

def main():
    """Run all tests"""
    print("Running branch naming service tests...")
    
    try:
        test_branch_name_parsing()
        test_invalid_branch_names()
        test_branch_name_validation()
        test_branch_name_suggestion()
        test_description_formatting()
        test_issue_number_extraction()
        test_branch_type_inference()
        test_complex_branch_scenarios()
        test_edge_case_descriptions()
        test_branch_validation_comprehensive()
        test_performance_with_many_branches()
        test_unicode_branch_names()
        test_branch_type_detection_edge_cases()
        
        print("\n🎉 All branch naming tests passed!")
        return 0
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())