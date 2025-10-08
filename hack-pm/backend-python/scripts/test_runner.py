#!/usr/bin/env python3
"""
Refactored comprehensive test runner for GitHub template system
Improved architecture, reporting, and configuration support
"""
import sys
import os
import time
import json
import traceback
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import argparse

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from tests.test_base import BaseTestSuite, PerformanceBenchmark
from src.utils.config import get_config, get_testing_config

@dataclass
class TestSuiteResult:
    """Result of running a test suite"""
    name: str
    success: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    total_time: float
    test_results: List[Dict[str, Any]] = field(default_factory=list)
    error_details: List[str] = field(default_factory=list)

@dataclass
class TestRunResult:
    """Result of running all test suites"""
    success: bool
    total_suites: int
    passed_suites: int
    failed_suites: int
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    total_time: float
    suite_results: List[TestSuiteResult] = field(default_factory=list)
    performance_stats: Dict[str, Any] = field(default_factory=dict)

class TestReporter:
    """Handles test result reporting in various formats"""
    
    def __init__(self, output_dir: str = "test_reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def print_summary(self, result: TestRunResult):
        """Print test run summary to console"""
        print(f"\n{'='*80}")
        print("TEST RUN SUMMARY")
        print(f"{'='*80}")
        
        # Overall results
        status_icon = "🎉" if result.success else "❌"
        print(f"{status_icon} Overall Result: {'PASSED' if result.success else 'FAILED'}")
        print(f"   Test Suites: {result.total_suites} total, {result.passed_suites} passed, {result.failed_suites} failed")
        print(f"   Test Cases: {result.total_tests} total, {result.passed_tests} passed, {result.failed_tests} failed")
        if result.skipped_tests > 0:
            print(f"   Skipped: {result.skipped_tests}")
        print(f"   Total Time: {result.total_time:.3f}s")
        success_rate = (result.passed_tests/result.total_tests)*100 if result.total_tests > 0 else 0
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Suite breakdown
        print(f"\n{'='*80}")
        print("SUITE BREAKDOWN")
        print(f"{'='*80}")
        
        for suite_result in result.suite_results:
            status_icon = "✅" if suite_result.success else "❌"
            print(f"{status_icon} {suite_result.name:<40} "
                  f"{suite_result.passed_tests}/{suite_result.total_tests} passed "
                  f"({suite_result.total_time:.3f}s)")
            
            # Show failed tests
            if not suite_result.success and suite_result.error_details:
                for error in suite_result.error_details[:3]:  # Show first 3 errors
                    print(f"    ❌ {error}")
                if len(suite_result.error_details) > 3:
                    print(f"    ... and {len(suite_result.error_details) - 3} more errors")
        
        # Performance stats
        if result.performance_stats:
            print(f"\n{'='*80}")
            print("PERFORMANCE STATISTICS")
            print(f"{'='*80}")
            
            for category, stats in result.performance_stats.items():
                print(f"{category}:")
                for metric, value in stats.items():
                    if isinstance(value, float):
                        print(f"  {metric}: {value:.4f}s")
                    else:
                        print(f"  {metric}: {value}")
        
        print(f"{'='*80}")
    
    def generate_json_report(self, result: TestRunResult, filename: str = "test_results.json"):
        """Generate JSON test report"""
        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "success": result.success,
            "summary": {
                "total_suites": result.total_suites,
                "passed_suites": result.passed_suites,
                "failed_suites": result.failed_suites,
                "total_tests": result.total_tests,
                "passed_tests": result.passed_tests,
                "failed_tests": result.failed_tests,
                "skipped_tests": result.skipped_tests,
                "total_time": result.total_time,
                "success_rate": (result.passed_tests/result.total_tests)*100 if result.total_tests > 0 else 0
            },
            "suites": [],
            "performance_stats": result.performance_stats
        }
        
        for suite_result in result.suite_results:
            suite_data = {
                "name": suite_result.name,
                "success": suite_result.success,
                "total_tests": suite_result.total_tests,
                "passed_tests": suite_result.passed_tests,
                "failed_tests": suite_result.failed_tests,
                "skipped_tests": suite_result.skipped_tests,
                "total_time": suite_result.total_time,
                "test_results": suite_result.test_results,
                "error_details": suite_result.error_details
            }
            report_data["suites"].append(suite_data)
        
        report_file = self.output_dir / filename
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"JSON report saved to: {report_file}")
    
    def generate_html_report(self, result: TestRunResult, filename: str = "test_results.html"):
        """Generate HTML test report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>GitHub Template System - Test Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .success {{ color: green; }}
        .failure {{ color: red; }}
        .suite {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .suite-header {{ font-weight: bold; font-size: 1.2em; margin-bottom: 10px; }}
        .test-result {{ margin: 5px 0; padding: 5px; }}
        .test-passed {{ background-color: #e8f5e8; }}
        .test-failed {{ background-color: #ffe8e8; }}
        .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
        .stat {{ padding: 10px; background-color: #f9f9f9; border-radius: 5px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GitHub Template System - Test Results</h1>
        <p>Generated: {time.strftime("%Y-%m-%d %H:%M:%S")}</p>
        <p class="{'success' if result.success else 'failure'}">
            Overall Result: {'PASSED' if result.success else 'FAILED'}
        </p>
    </div>
    
    <div class="stats">
        <div class="stat">
            <strong>Test Suites</strong><br>
            {result.total_suites} total<br>
            {result.passed_suites} passed<br>
            {result.failed_suites} failed
        </div>
        <div class="stat">
            <strong>Test Cases</strong><br>
            {result.total_tests} total<br>
            {result.passed_tests} passed<br>
            {result.failed_tests} failed
        </div>
        <div class="stat">
            <strong>Performance</strong><br>
            Total Time: {result.total_time:.3f}s<br>
            Success Rate: {(result.passed_tests/result.total_tests)*100 if result.total_tests > 0 else 0:.1f}%
        </div>
    </div>
"""
        
        # Add suite details
        for suite_result in result.suite_results:
            suite_class = "success" if suite_result.success else "failure"
            html_content += f"""
    <div class="suite">
        <div class="suite-header {suite_class}">
            {suite_result.name} - {suite_result.passed_tests}/{suite_result.total_tests} passed ({suite_result.total_time:.3f}s)
        </div>
"""
            
            # Add test results
            for test_result in suite_result.test_results:
                test_class = "test-passed" if test_result.get("success", False) else "test-failed"
                html_content += f"""
        <div class="test-result {test_class}">
            {test_result.get("name", "Unknown Test")} - {test_result.get("duration", 0):.3f}s
            {f"<br><small>Error: {test_result.get('error', '')}</small>" if test_result.get("error") else ""}
        </div>
"""
            
            html_content += "    </div>\n"
        
        # Add performance stats
        if result.performance_stats:
            html_content += """
    <h2>Performance Statistics</h2>
    <table>
        <tr><th>Category</th><th>Metric</th><th>Value</th></tr>
"""
            for category, stats in result.performance_stats.items():
                for metric, value in stats.items():
                    formatted_value = f"{value:.4f}s" if isinstance(value, float) else str(value)
                    html_content += f"        <tr><td>{category}</td><td>{metric}</td><td>{formatted_value}</td></tr>\n"
            
            html_content += "    </table>\n"
        
        html_content += """
</body>
</html>
"""
        
        report_file = self.output_dir / filename
        with open(report_file, 'w') as f:
            f.write(html_content)
        
        print(f"HTML report saved to: {report_file}")

class RefactoredTestRunner:
    """Improved test runner with better architecture and reporting"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = get_config()
        self.testing_config = get_testing_config()
        self.reporter = TestReporter()
        self.performance_tracker = PerformanceBenchmark("Overall Test Run")
        
    def discover_test_suites(self, test_dir: str = "tests") -> List[str]:
        """Discover test suite files"""
        test_files = []
        
        # Look for test files in tests directory
        tests_path = Path(test_dir)
        if tests_path.exists():
            for file_path in tests_path.glob("test_*.py"):
                if file_path.name != "test_base.py":
                    test_files.append(str(file_path))
        
        # Fallback to current directory if tests directory doesn't exist
        if not test_files:
            for file_path in Path(".").glob("test_*.py"):
                if file_path.name != "test_base.py":
                    test_files.append(str(file_path))
        
        return sorted(test_files)
    
    def run_test_suite_file(self, test_file: str) -> TestSuiteResult:
        """Run a test suite from a file"""
        suite_name = Path(test_file).stem.replace("test_", "").replace("_", " ").title()
        
        try:
            # Import the test module
            module_name = Path(test_file).stem
            spec = __import__(module_name)
            
            # Look for a main function or test suite class
            if hasattr(spec, 'main'):
                start_time = time.time()
                result_code = spec.main()
                end_time = time.time()
                
                # Create a basic result (we don't have detailed info from main())
                success = result_code == 0
                return TestSuiteResult(
                    name=suite_name,
                    success=success,
                    total_tests=1,  # We don't know the actual count
                    passed_tests=1 if success else 0,
                    failed_tests=0 if success else 1,
                    skipped_tests=0,
                    total_time=end_time - start_time,
                    test_results=[{
                        "name": suite_name,
                        "success": success,
                        "duration": end_time - start_time
                    }]
                )
            else:
                # No main function found
                return TestSuiteResult(
                    name=suite_name,
                    success=False,
                    total_tests=0,
                    passed_tests=0,
                    failed_tests=0,
                    skipped_tests=1,
                    total_time=0.0,
                    error_details=["No main() function found in test file"]
                )
                
        except Exception as e:
            return TestSuiteResult(
                name=suite_name,
                success=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                total_time=0.0,
                error_details=[f"Failed to run test suite: {str(e)}"]
            )
    
    def run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks"""
        if not self.testing_config.enable_performance_tests:
            return {}
        
        benchmarks = {}
        
        try:
            # Import modules for benchmarking
            from src.core.template_parser import TemplateParser
            from tests.test_base import MockDataGenerator
            
            parser = TemplateParser()
            mock_data = MockDataGenerator()
            
            # Benchmark template parsing
            with PerformanceBenchmark("Template Parsing") as benchmark:
                template = mock_data.create_yaml_template()
                
                parse_stats = benchmark.measure_operation(
                    lambda: parser.parse_issue_body(template, ["feature"]),
                    iterations=100
                )
                
                benchmarks["template_parsing"] = parse_stats
            
            # Benchmark large template parsing
            with PerformanceBenchmark("Large Template Parsing") as benchmark:
                large_template = mock_data.create_yaml_template(
                    acceptance_criteria=[f"Criterion {i}" for i in range(50)],
                    technical_requirements=[f"Requirement {i}" for i in range(25)]
                )
                
                large_parse_stats = benchmark.measure_operation(
                    lambda: parser.parse_issue_body(large_template, ["feature"]),
                    iterations=10
                )
                
                benchmarks["large_template_parsing"] = large_parse_stats
            
        except Exception as e:
            benchmarks["error"] = str(e)
        
        return benchmarks
    
    def run_all_tests(self, test_files: Optional[List[str]] = None) -> TestRunResult:
        """Run all test suites"""
        if test_files is None:
            test_files = self.discover_test_suites()
        
        print(f"🚀 Starting GitHub Template System Test Run")
        print(f"Environment: {self.config.environment}")
        print(f"Test files: {len(test_files)}")
        print(f"Configuration: {self.config.log_level} logging, "
              f"{'debug' if self.config.debug_mode else 'normal'} mode")
        print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        start_time = time.time()
        suite_results = []
        
        # Run each test suite
        for test_file in test_files:
            print(f"\n{'='*60}")
            print(f"Running {Path(test_file).stem}")
            print(f"{'='*60}")
            
            suite_result = self.run_test_suite_file(test_file)
            suite_results.append(suite_result)
            
            # Print immediate feedback
            status = "✅ PASSED" if suite_result.success else "❌ FAILED"
            print(f"{status} - {suite_result.name} ({suite_result.total_time:.3f}s)")
        
        # Run performance benchmarks
        performance_stats = self.run_performance_benchmarks()
        
        total_time = time.time() - start_time
        
        # Calculate totals
        total_suites = len(suite_results)
        passed_suites = sum(1 for r in suite_results if r.success)
        failed_suites = total_suites - passed_suites
        
        total_tests = sum(r.total_tests for r in suite_results)
        passed_tests = sum(r.passed_tests for r in suite_results)
        failed_tests = sum(r.failed_tests for r in suite_results)
        skipped_tests = sum(r.skipped_tests for r in suite_results)
        
        result = TestRunResult(
            success=failed_suites == 0,
            total_suites=total_suites,
            passed_suites=passed_suites,
            failed_suites=failed_suites,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            total_time=total_time,
            suite_results=suite_results,
            performance_stats=performance_stats
        )
        
        return result

def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(description="GitHub Template System Test Runner")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--output-dir", default="test_reports", help="Output directory for reports")
    parser.add_argument("--format", choices=["console", "json", "html", "all"], default="all",
                       help="Report format")
    parser.add_argument("--test-files", nargs="*", help="Specific test files to run")
    parser.add_argument("--no-performance", action="store_true", help="Skip performance benchmarks")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = RefactoredTestRunner(args.config)
    runner.reporter = TestReporter(args.output_dir)
    
    # Override performance testing if requested
    if args.no_performance:
        runner.testing_config.enable_performance_tests = False
    
    # Run tests
    result = runner.run_all_tests(args.test_files)
    
    # Generate reports
    if args.format in ["console", "all"]:
        runner.reporter.print_summary(result)
    
    if args.format in ["json", "all"]:
        runner.reporter.generate_json_report(result)
    
    if args.format in ["html", "all"]:
        runner.reporter.generate_html_report(result)
    
    # Return appropriate exit code
    return 0 if result.success else 1

if __name__ == "__main__":
    sys.exit(main())