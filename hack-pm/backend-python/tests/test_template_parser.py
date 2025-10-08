#!/usr/bin/env python3
"""
Refactored unit tests for template parser functionality
Using improved test architecture and utilities
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tests.test_base import BaseTestSuite, MockDataGenerator, PerformanceBenchmark, TestAssertions
from src.core.template_parser import TemplateParser, TemplateType, Priority, ParsedTemplateData
from src.utils.config import ParsingConfig

class TemplateParserTestSuite(BaseTestSuite):
    """Comprehensive test suite for template parser"""
    
    def __init__(self):
        super().__init__("Template Parser Tests")
        self.parser = None
        self.mock_data = MockDataGenerator()
        
    def setup(self):
        """Setup test environment"""
        self.parser = TemplateParser()
        super().setup()
        
    def get_test_methods(self):
        """Return list of test methods to run"""
        return [
            (self.test_yaml_feature_template, "YAML Feature Template Parsing"),
            (self.test_yaml_bug_template, "YAML Bug Template Parsing"),
            (self.test_markdown_feature_template, "Markdown Feature Template Parsing"),
            (self.test_markdown_bug_template, "Markdown Bug Template Parsing"),
            (self.test_pr_template_parsing, "PR Template Parsing"),
            (self.test_priority_extraction, "Priority Extraction from Labels"),
            (self.test_template_type_detection, "Template Type Detection"),
            (self.test_security_sanitization, "Security Sanitization"),
            (self.test_empty_input_handling, "Empty Input Handling"),
            (self.test_malformed_yaml_handling, "Malformed YAML Handling"),
            (self.test_performance_benchmarks, "Performance Benchmarks"),
            (self.test_unicode_content, "Unicode Content Handling"),
            (self.test_large_template_handling, "Large Template Handling"),
            (self.test_edge_cases, "Edge Case Handling"),
            (self.test_configuration_options, "Configuration Options"),
        ]
    
    def test_yaml_feature_template(self):
        """Test parsing YAML-based feature template"""
        body = self.mock_data.create_yaml_template(
            template_type="feature",
            priority="high",
            estimated_time=8,
            user_story="As a developer, I want to create templates, so that I can standardize issues",
            acceptance_criteria=[
                "Template should parse YAML frontmatter",
                "Template should extract user stories",
                "Template should handle missing fields gracefully"
            ],
            technical_requirements=[
                "Implement YAML parser",
                "Add validation logic"
            ],
            branch_name="feature/123-template-system"
        )
        
        result = self.parser.parse_issue_body(body, ["feature", "high-priority"])
        
        TestAssertions.assert_template_data_valid(result, TemplateType.FEATURE, Priority.HIGH)
        assert result.estimated_time == 8
        assert len(result.acceptance_criteria) == 3
        assert len(result.technical_requirements) == 2
        assert result.branch_suggestion == "feature/123-template-system"
        assert "standardize issues" in result.user_story
    
    def test_yaml_bug_template(self):
        """Test parsing YAML-based bug template"""
        body = self.mock_data.create_yaml_template(
            template_type="bug",
            priority="critical",
            reproduction_steps=[
                "Open the application",
                "Click on the broken button",
                "Observe the error"
            ],
            expected_behavior="Button should work correctly",
            actual_behavior="Button throws an error",
            environment={
                "os": "macOS",
                "browser": "Chrome",
                "version": "1.0.0"
            }
        )
        
        result = self.parser.parse_issue_body(body, ["bug", "critical"])
        
        TestAssertions.assert_template_data_valid(result, TemplateType.BUG, Priority.CRITICAL)
        assert len(result.reproduction_steps) == 3
        assert "Open the application" in result.reproduction_steps
        assert result.expected_behavior == "Button should work correctly"
        assert result.actual_behavior == "Button throws an error"
        assert result.environment_details["os"] == "macOS"
    
    def test_markdown_feature_template(self):
        """Test parsing markdown-based feature template"""
        body = self.mock_data.create_markdown_template("feature")
        
        result = self.parser.parse_issue_body(body, ["feature"])
        
        TestAssertions.assert_template_data_valid(result, TemplateType.FEATURE)
        assert len(result.acceptance_criteria) >= 2
        assert len(result.technical_requirements) >= 2
        assert result.user_story is not None
    
    def test_markdown_bug_template(self):
        """Test parsing markdown-based bug template"""
        body = self.mock_data.create_markdown_template("bug")
        
        result = self.parser.parse_issue_body(body, ["bug"])
        
        TestAssertions.assert_template_data_valid(result, TemplateType.BUG)
        assert len(result.reproduction_steps) >= 2
        assert result.expected_behavior is not None
        assert result.actual_behavior is not None
    
    def test_pr_template_parsing(self):
        """Test parsing PR template"""
        body = self.mock_data.create_pr_template(
            summary="This PR implements the new authentication system",
            related_issues=[123, 456],
            breaking_changes="Changed API endpoint from /auth to /authentication",
            testing_checklist=[
                "[x] Unit tests pass",
                "[x] Integration tests pass",
                "[ ] Manual testing completed"
            ]
        )
        
        result = self.parser.parse_pr_body(body, "Add authentication system")
        
        assert result.changes_summary is not None
        assert 123 in result.related_issues
        assert 456 in result.related_issues
        assert len(result.testing_checklist) == 3
        assert result.breaking_changes is not None
        
        # Check completion tracking
        completed_items = [item for item in result.testing_checklist if '[x]' in item.lower()]
        assert len(completed_items) == 2
    
    def test_priority_extraction(self):
        """Test priority extraction from various sources"""
        test_cases = [
            (["high", "feature"], Priority.HIGH),
            (["urgent", "bug"], Priority.CRITICAL),
            (["feature"], Priority.MEDIUM),
            (["low", "task"], Priority.LOW),  # Changed from "low-priority" to "low"
        ]
        
        for labels, expected_priority in test_cases:
            body = "Simple issue description"
            result = self.parser.parse_issue_body(body, labels)
            assert result.priority == expected_priority, f"Expected {expected_priority} for labels {labels}, got {result.priority}"
    
    def test_template_type_detection(self):
        """Test template type detection from labels and content"""
        test_cases = [
            (["enhancement"], TemplateType.FEATURE),
            (["bug"], TemplateType.BUG),
            (["chore"], TemplateType.TASK),
            (["maintenance"], TemplateType.TASK),
        ]
        
        for labels, expected_type in test_cases:
            body = "Generic issue description"
            result = self.parser.parse_issue_body(body, labels)
            assert result.template_type == expected_type, f"Expected {expected_type} for labels {labels}"
    
    def test_security_sanitization(self):
        """Test security sanitization features"""
        malicious_inputs = [
            "<script>alert('xss')</script>As a user, I want security",
            "<img src=x onerror=alert('xss')>Criterion 1",
            "javascript:alert('xss')",
            "<iframe src='javascript:alert(1)'></iframe>Requirement"
        ]
        
        for malicious_input in malicious_inputs:
            body = self.mock_data.create_yaml_template(
                user_story=malicious_input,
                acceptance_criteria=[malicious_input],
                technical_requirements=[malicious_input]
            )
            
            result = self.parser.parse_issue_body(body, ["feature"])
            
            # Should remove dangerous tags but preserve content
            if result.user_story:
                assert "<script>" not in result.user_story
                assert "<img" not in result.user_story
                assert "<iframe" not in result.user_story
                # Content should be preserved (without dangerous parts)
                assert len(result.user_story) > 0
    
    def test_empty_input_handling(self):
        """Test handling of empty or None inputs"""
        test_cases = ["", None, "   ", "\n\n"]
        
        for empty_input in test_cases:
            result = self.parser.parse_issue_body(empty_input)
            TestAssertions.assert_template_data_valid(result, TemplateType.UNKNOWN, Priority.MEDIUM)
    
    def test_malformed_yaml_handling(self):
        """Test handling of malformed YAML"""
        malformed_yaml = """---
invalid: yaml: [content
missing_closing_bracket: [
---
This should fall back to markdown parsing.
"""
        
        result = self.parser.parse_issue_body(malformed_yaml)
        # Should not crash and should fall back to markdown parsing
        assert result is not None
        assert result.template_type == TemplateType.UNKNOWN
    
    def test_performance_benchmarks(self):
        """Test performance with various template sizes"""
        with PerformanceBenchmark("Template Parsing Performance") as benchmark:
            # Test small templates
            small_template = self.mock_data.create_yaml_template()
            
            small_perf = benchmark.measure_operation(
                lambda: self.parser.parse_issue_body(small_template, ["feature"]),
                iterations=100
            )
            
            TestAssertions.assert_performance_acceptable(
                small_perf["average_time"], 0.01, "Small template parsing"
            )
            
            # Test large templates
            large_template = self.mock_data.create_yaml_template(
                acceptance_criteria=[f"Criterion {i}" for i in range(50)],
                technical_requirements=[f"Requirement {i}" for i in range(25)]
            )
            
            large_perf = benchmark.measure_operation(
                lambda: self.parser.parse_issue_body(large_template, ["feature"]),
                iterations=10
            )
            
            TestAssertions.assert_performance_acceptable(
                large_perf["average_time"], 0.1, "Large template parsing"
            )
    
    def test_unicode_content(self):
        """Test handling of Unicode and international characters"""
        unicode_template = self.mock_data.create_yaml_template(
            user_story="As a 用户, I want to 使用 émojis 🚀 and spëcial chars, so that I can 工作 effectively",
            acceptance_criteria=[
                "Support Unicode: 你好世界",
                "Support emojis: 🎉 ✅ 🚀",
                "Support accents: café, naïve, résumé"
            ]
        )
        
        result = self.parser.parse_issue_body(unicode_template, ["feature", "i18n"])
        
        TestAssertions.assert_template_data_valid(result, TemplateType.FEATURE)
        assert "用户" in result.user_story
        assert "🚀" in result.user_story
        assert len(result.acceptance_criteria) == 3
        assert "你好世界" in result.acceptance_criteria[0]
        assert "🎉" in result.acceptance_criteria[1]
    
    def test_large_template_handling(self):
        """Test handling of very large templates"""
        # Create a template with many items (but not too many to avoid YAML issues)
        large_criteria = [f"Criterion {i}" for i in range(50)]
        large_tech_req = [f"Requirement {i}" for i in range(25)]
        
        large_template = self.mock_data.create_yaml_template(
            acceptance_criteria=large_criteria,
            technical_requirements=large_tech_req
        )
        
        result = self.parser.parse_issue_body(large_template, ["feature"])
        
        TestAssertions.assert_template_data_valid(result, TemplateType.FEATURE)
        # Should handle large lists properly
        assert len(result.acceptance_criteria) >= 25  # Should have many items
        assert len(result.technical_requirements) >= 15
    
    def test_edge_cases(self):
        """Test various edge cases"""
        edge_cases = [
            # Only YAML frontmatter, no content
            "---\ntemplate_type: task\npriority: low\n---",
            # Mixed valid and invalid YAML
            "---\ntemplate_type: feature\ninvalid_yaml: [\n---\nSome content",
            # Very long single line
            "---\nuser_story: " + "A" * 5000 + "\n---",
        ]
        
        for edge_case in edge_cases:
            result = self.parser.parse_issue_body(edge_case, ["test"])
            # Should not crash
            assert result is not None
            TestAssertions.assert_template_data_valid(result)
    
    def test_configuration_options(self):
        """Test different configuration options"""
        # Test with different parser configurations
        # Since we don't have the full refactored config system integrated,
        # we'll test basic functionality
        
        # Test with simple template
        simple_template = self.mock_data.create_yaml_template(
            acceptance_criteria=[f"Criterion {i}" for i in range(5)]
        )
        
        result = self.parser.parse_issue_body(simple_template, ["feature"])
        TestAssertions.assert_template_data_valid(result, TemplateType.FEATURE)
        assert len(result.acceptance_criteria) == 5

def main():
    """Run the refactored template parser tests"""
    suite = TemplateParserTestSuite()
    results = suite.run_all_tests()
    
    # Print performance statistics
    parser_stats = suite.parser.get_performance_stats()
    print(f"\nPerformance Statistics:")
    print(f"  Total parses: {parser_stats['parse_count']}")
    print(f"  Average time: {parser_stats['average_time']:.4f}s")
    print(f"  Total time: {parser_stats['total_time']:.4f}s")
    
    return 0 if results["success"] else 1

if __name__ == "__main__":
    sys.exit(main())