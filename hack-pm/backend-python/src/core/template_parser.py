"""
Template parsing service for GitHub issue and PR templates
Refactored for improved structure, performance, and maintainability
"""
import re
import yaml
import json
import logging
from typing import Dict, Any, List, Optional, Union, Pattern
from dataclasses import dataclass, field
from enum import Enum
from functools import lru_cache
import time

logger = logging.getLogger(__name__)

class TemplateType(Enum):
    FEATURE = "feature"
    BUG = "bug"
    TASK = "task"
    UNKNOWN = "unknown"

class Priority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class ParsedTemplateData:
    """Structured data extracted from GitHub issue/PR templates"""
    template_type: TemplateType
    priority: Priority
    estimated_time: Optional[int] = None
    acceptance_criteria: List[str] = field(default_factory=list)
    technical_requirements: List[str] = field(default_factory=list)
    branch_suggestion: Optional[str] = None
    user_story: Optional[str] = None
    reproduction_steps: List[str] = field(default_factory=list)
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    environment_details: Dict[str, str] = field(default_factory=dict)
    task_checklist: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    breaking_changes: Optional[str] = None
    testing_checklist: List[str] = field(default_factory=list)
    related_issues: List[int] = field(default_factory=list)
    changes_summary: Optional[str] = None
    deployment_notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate data after initialization"""
        self._validate_and_sanitize()
    
    def _validate_and_sanitize(self):
        """Validate and sanitize all data fields"""
        # Validate estimated time
        if self.estimated_time is not None and self.estimated_time < 0:
            self.estimated_time = None
            
        # Ensure priority is valid
        if not isinstance(self.priority, Priority):
            self.priority = Priority.MEDIUM

class TemplateParser:
    """Parser for GitHub issue and PR templates with improved architecture"""
    
    def __init__(self, config=None):
        # Import config here to avoid circular imports
        try:
            from src.utils.config import ParsingConfig
            self.config = config or ParsingConfig()
        except ImportError:
            # Fallback configuration if config module not available
            self.config = type('Config', (), {
                'max_text_length': 10000,
                'max_list_items': 100,
                'sanitization_enabled': True,
                'cache_size': 128
            })()
        
        # Pre-compiled regex patterns for performance
        self.yaml_frontmatter_pattern = re.compile(
            r'^---\s*\n(.*?)\n---\s*(?:\n(.*))?', 
            re.DOTALL | re.MULTILINE
        )
        self.checkbox_pattern = re.compile(r'^\s*-\s*\[[ xX]\]\s*(.+)', re.MULTILINE | re.IGNORECASE)
        self.numbered_list_pattern = re.compile(r'^\s*\d+\.\s*(.+)', re.MULTILINE)
        self.bullet_list_pattern = re.compile(r'^\s*[-*+]\s*(.+)', re.MULTILINE)
        self.issue_reference_pattern = re.compile(
            r'(?:fixes?|closes?|resolves?|relates?\s+to|#)\s*#?(\d+)', 
            re.IGNORECASE
        )
        
        self.priority_keywords = {
            'critical': Priority.CRITICAL,
            'high': Priority.HIGH,
            'medium': Priority.MEDIUM,
            'low': Priority.LOW,
            'urgent': Priority.CRITICAL,
            'important': Priority.HIGH,
            'normal': Priority.MEDIUM,
            'minor': Priority.LOW
        }
        
        # Performance tracking
        self.parse_count = 0
        self.total_parse_time = 0.0
    
    def parse_issue_body(self, body: str, labels: List[str] = None) -> ParsedTemplateData:
        """
        Parse GitHub issue body to extract structured template data
        
        Args:
            body: The issue body text
            labels: List of issue labels
            
        Returns:
            ParsedTemplateData object with extracted information
        """
        start_time = time.time()
        
        try:
            if not body:
                return ParsedTemplateData(
                    template_type=TemplateType.UNKNOWN,
                    priority=Priority.MEDIUM
                )
            
            # Try to parse YAML frontmatter first
            yaml_data = self._extract_yaml_frontmatter(body)
            if yaml_data:
                result = self._parse_yaml_template(yaml_data, body, labels)
            else:
                # Fall back to markdown parsing
                result = self._parse_markdown_template(body, labels)
            
            return result
            
        finally:
            # Track performance
            self.parse_count += 1
            self.total_parse_time += time.time() - start_time
    
    def parse_pr_body(self, body: str, title: str = None) -> ParsedTemplateData:
        """
        Parse GitHub PR body to extract structured template data
        
        Args:
            body: The PR body text
            title: The PR title
            
        Returns:
            ParsedTemplateData object with extracted information
        """
        if not body:
            return ParsedTemplateData(
                template_type=TemplateType.UNKNOWN,
                priority=Priority.MEDIUM
            )
        
        # Extract PR-specific information
        data = ParsedTemplateData(
            template_type=TemplateType.UNKNOWN,
            priority=Priority.MEDIUM
        )
        
        # Extract changes summary
        data.changes_summary = self._extract_section(body, ["changes", "summary", "description"])
        
        # Extract related issues
        data.related_issues = self._extract_issue_references(body)
        
        # Extract testing checklist (preserve checkbox markers for completion tracking)
        data.testing_checklist = self._extract_checklist_items(body, ["testing", "test"])
        
        # Extract breaking changes
        data.breaking_changes = self._extract_section(body, ["breaking", "breaking changes"])
        
        # Extract deployment notes
        data.deployment_notes = self._extract_section(body, ["deployment", "deploy"])
        
        return data
    
    def _extract_yaml_frontmatter(self, body: str) -> Optional[Dict[str, Any]]:
        """Extract YAML frontmatter from issue body"""
        try:
            match = self.yaml_frontmatter_pattern.match(body.strip())
            if match:
                yaml_content = match.group(1)
                return yaml.safe_load(yaml_content)
        except (yaml.YAMLError, AttributeError) as e:
            logger.warning(f"Failed to parse YAML frontmatter: {e}")
        return None
    
    def _parse_yaml_template(self, yaml_data: Dict[str, Any], body: str, labels: List[str] = None) -> ParsedTemplateData:
        """Parse YAML-based template data"""
        data = ParsedTemplateData(
            template_type=self._determine_template_type(yaml_data, labels),
            priority=self._extract_priority(yaml_data, labels)
        )
        
        # Extract common fields
        data.estimated_time = self._safe_int(yaml_data.get('estimated_time'))
        data.user_story = self._sanitize_text(yaml_data.get('user_story'))
        data.branch_suggestion = self._sanitize_text(yaml_data.get('branch_name'))
        
        # Extract acceptance criteria
        criteria = yaml_data.get('acceptance_criteria', [])
        if isinstance(criteria, list):
            data.acceptance_criteria = [self._sanitize_text(item) for item in criteria if item]
        elif isinstance(criteria, str):
            data.acceptance_criteria = self._extract_list_items(criteria)
        
        # Extract technical requirements
        tech_req = yaml_data.get('technical_requirements', [])
        if isinstance(tech_req, list):
            data.technical_requirements = [self._sanitize_text(item) for item in tech_req if item]
        elif isinstance(tech_req, str):
            data.technical_requirements = self._extract_list_items(tech_req)
        
        # Template-specific parsing
        if data.template_type == TemplateType.BUG:
            repro_steps = yaml_data.get('reproduction_steps', [])
            if isinstance(repro_steps, list):
                data.reproduction_steps = [self._sanitize_text(step) for step in repro_steps if step]
            else:
                data.reproduction_steps = self._extract_list_items(str(repro_steps))
            data.expected_behavior = self._sanitize_text(yaml_data.get('expected_behavior'))
            data.actual_behavior = self._sanitize_text(yaml_data.get('actual_behavior'))
            data.environment_details = self._extract_environment_details(yaml_data.get('environment', {}))
        
        elif data.template_type == TemplateType.TASK:
            data.task_checklist = self._extract_list_items(yaml_data.get('checklist', ''))
            data.dependencies = self._extract_list_items(yaml_data.get('dependencies', ''))
        
        return data
    
    def _parse_markdown_template(self, body: str, labels: List[str] = None) -> ParsedTemplateData:
        """Parse markdown-based template data"""
        data = ParsedTemplateData(
            template_type=self._determine_template_type_from_content(body, labels),
            priority=self._extract_priority_from_content(body, labels)
        )
        
        # Extract sections based on headers
        sections = self._extract_markdown_sections(body)
        
        # Extract acceptance criteria
        data.acceptance_criteria = self._extract_acceptance_criteria(sections)
        
        # Extract technical requirements
        data.technical_requirements = self._extract_technical_requirements(sections)
        
        # Extract user story
        data.user_story = self._extract_user_story(sections)
        
        # Extract bug-specific information
        if data.template_type == TemplateType.BUG:
            data.reproduction_steps = self._extract_reproduction_steps(sections)
            data.expected_behavior = sections.get('expected behavior') or sections.get('expected')
            data.actual_behavior = sections.get('actual behavior') or sections.get('actual')
        
        # Extract task checklist
        if data.template_type == TemplateType.TASK:
            data.task_checklist = self._extract_task_checklist(sections)
        
        return data
    
    def _determine_template_type(self, yaml_data: Dict[str, Any], labels: List[str] = None) -> TemplateType:
        """Determine template type from YAML data and labels"""
        # Check explicit template type
        template_type = yaml_data.get('template_type', '').lower()
        if template_type in ['feature', 'enhancement']:
            return TemplateType.FEATURE
        elif template_type in ['bug', 'bugfix']:
            return TemplateType.BUG
        elif template_type in ['task', 'chore']:
            return TemplateType.TASK
        
        # Check labels
        if labels:
            label_names = [label.lower() for label in labels]
            if any(label in ['feature', 'enhancement', 'new feature'] for label in label_names):
                return TemplateType.FEATURE
            elif any(label in ['bug', 'bugfix', 'defect'] for label in label_names):
                return TemplateType.BUG
            elif any(label in ['task', 'chore', 'maintenance'] for label in label_names):
                return TemplateType.TASK
        
        return TemplateType.UNKNOWN
    
    def _determine_template_type_from_content(self, body: str, labels: List[str] = None) -> TemplateType:
        """Determine template type from content analysis"""
        body_lower = body.lower()
        
        # Check for bug indicators
        bug_indicators = ['reproduction steps', 'expected behavior', 'actual behavior', 'bug report']
        if any(indicator in body_lower for indicator in bug_indicators):
            return TemplateType.BUG
        
        # Check for feature indicators
        feature_indicators = ['user story', 'acceptance criteria', 'feature request']
        if any(indicator in body_lower for indicator in feature_indicators):
            return TemplateType.FEATURE
        
        # Check for task indicators
        task_indicators = ['checklist', 'todo', 'task list']
        if any(indicator in body_lower for indicator in task_indicators):
            return TemplateType.TASK
        
        # Fall back to label analysis
        if labels:
            return self._determine_template_type({}, labels)
        
        return TemplateType.UNKNOWN
    
    def _extract_priority(self, yaml_data: Dict[str, Any], labels: List[str] = None) -> Priority:
        """Extract priority from YAML data and labels"""
        # Check explicit priority field
        priority = yaml_data.get('priority', '').lower()
        if priority in self.priority_keywords:
            return self.priority_keywords[priority]
        
        # Check labels
        if labels:
            for label in labels:
                label_lower = label.lower()
                if label_lower in self.priority_keywords:
                    return self.priority_keywords[label_lower]
        
        return Priority.MEDIUM
    
    def _extract_priority_from_content(self, body: str, labels: List[str] = None) -> Priority:
        """Extract priority from content analysis"""
        body_lower = body.lower()
        
        # Check for priority keywords in content
        for keyword, priority in self.priority_keywords.items():
            if keyword in body_lower:
                return priority
        
        # Fall back to label analysis
        if labels:
            return self._extract_priority({}, labels)
        
        return Priority.MEDIUM 
   
    def _extract_markdown_sections(self, body: str) -> Dict[str, str]:
        """Extract sections from markdown content based on headers"""
        sections = {}
        current_section = None
        current_content = []
        
        lines = body.split('\n')
        for line in lines:
            # Check for headers (# ## ### etc.)
            if line.strip().startswith('#'):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.strip('#').strip().lower()
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _extract_acceptance_criteria(self, sections: Dict[str, str]) -> List[str]:
        """Extract acceptance criteria from sections"""
        criteria_section = sections.get('acceptance criteria') or sections.get('acceptance')
        if not criteria_section:
            return []
        
        return self._extract_list_items(criteria_section)
    
    def _extract_technical_requirements(self, sections: Dict[str, str]) -> List[str]:
        """Extract technical requirements from sections"""
        tech_section = sections.get('technical requirements') or sections.get('technical')
        if not tech_section:
            return []
        
        return self._extract_list_items(tech_section)
    
    def _extract_user_story(self, sections: Dict[str, str]) -> Optional[str]:
        """Extract user story from sections"""
        story_section = sections.get('user story') or sections.get('story')
        if story_section:
            return self._sanitize_text(story_section)
        return None
    
    def _extract_reproduction_steps(self, sections: Dict[str, str]) -> List[str]:
        """Extract reproduction steps from sections"""
        repro_section = sections.get('reproduction steps') or sections.get('steps to reproduce')
        if not repro_section:
            return []
        
        return self._extract_list_items(repro_section)
    
    def _extract_task_checklist(self, sections: Dict[str, str]) -> List[str]:
        """Extract task checklist from sections"""
        checklist_section = sections.get('checklist') or sections.get('tasks')
        if not checklist_section:
            return []
        
        return self._extract_checklist_items(checklist_section)
    
    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items from text (numbered or bulleted)"""
        if not text:
            return []
        
        items = []
        
        # Extract numbered list items
        numbered_matches = self.numbered_list_pattern.findall(text)
        items.extend([self._sanitize_text(item) for item in numbered_matches])
        
        # Extract bulleted list items
        bullet_pattern = re.compile(r'^\s*[-*+]\s*(.+)', re.MULTILINE)
        bullet_matches = bullet_pattern.findall(text)
        items.extend([self._sanitize_text(item) for item in bullet_matches])
        
        return [item for item in items if item]
    
    def _extract_checklist_items(self, text: str, keywords: List[str] = None) -> List[str]:
        """Extract checkbox items from text (preserving checkbox markers for completion tracking)"""
        if not text:
            return []
        
        # If keywords provided, first try to find a section with those keywords
        if keywords:
            sections = self._extract_markdown_sections(text)
            for keyword in keywords:
                for section_name, content in sections.items():
                    if keyword in section_name.lower():
                        text = content
                        break
        
        # Find all checkbox items and preserve the full line including checkbox markers
        checkbox_items = []
        lines = text.split('\n')
        for line in lines:
            # Match checkbox patterns and preserve the full line
            if re.match(r'^\s*-\s*\[[ xX]\]\s*(.+)', line.strip(), re.IGNORECASE):
                checkbox_items.append(self._sanitize_text(line.strip()))
        
        return checkbox_items
    
    def _extract_section(self, body: str, keywords: List[str]) -> Optional[str]:
        """Extract content from a section matching keywords"""
        sections = self._extract_markdown_sections(body)
        
        for keyword in keywords:
            for section_name, content in sections.items():
                if keyword in section_name.lower():
                    return self._sanitize_text(content)
        
        return None
    
    def _extract_issue_references(self, text: str) -> List[int]:
        """Extract issue number references from text"""
        if not text:
            return []
        
        # Pattern to match #123, fixes #123, closes #123, etc.
        issue_pattern = re.compile(r'(?:fixes?|closes?|resolves?|relates?\s+to|#)\s*#?(\d+)', re.IGNORECASE)
        matches = issue_pattern.findall(text)
        
        return [int(match) for match in matches if match.isdigit()]
    
    def _extract_environment_details(self, env_data: Union[Dict, str]) -> Dict[str, str]:
        """Extract environment details from various formats"""
        if isinstance(env_data, dict):
            return {k: self._sanitize_text(str(v)) for k, v in env_data.items()}
        
        if isinstance(env_data, str):
            # Try to parse key-value pairs from text
            details = {}
            lines = env_data.split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    details[key.strip()] = self._sanitize_text(value.strip())
            return details
        
        return {}
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text input for security"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters and normalize whitespace
        sanitized = re.sub(r'[<>"\']', '', str(text))
        sanitized = re.sub(r'\s+', ' ', sanitized)
        return sanitized.strip()
    
    def _safe_int(self, value: Any) -> Optional[int]:
        """Safely convert value to integer"""
        if value is None:
            return None
        
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def validate_parsed_data(self, data: ParsedTemplateData) -> ParsedTemplateData:
        """Validate and apply defaults to parsed data"""
        # Ensure lists are not None
        if data.acceptance_criteria is None:
            data.acceptance_criteria = []
        if data.technical_requirements is None:
            data.technical_requirements = []
        if data.reproduction_steps is None:
            data.reproduction_steps = []
        if data.task_checklist is None:
            data.task_checklist = []
        if data.dependencies is None:
            data.dependencies = []
        if data.testing_checklist is None:
            data.testing_checklist = []
        if data.related_issues is None:
            data.related_issues = []
        if data.environment_details is None:
            data.environment_details = {}
        
        # Validate estimated time
        if data.estimated_time is not None and data.estimated_time < 0:
            data.estimated_time = None
        
        # Ensure priority is valid
        if not isinstance(data.priority, Priority):
            data.priority = Priority.MEDIUM
        
        return data
    
    def get_performance_stats(self) -> Dict[str, float]:
        """Get performance statistics"""
        if self.parse_count == 0:
            return {"parse_count": 0, "average_time": 0.0, "total_time": 0.0}
        
        return {
            "parse_count": self.parse_count,
            "average_time": self.total_parse_time / self.parse_count,
            "total_time": self.total_parse_time
        }
    
    def reset_performance_stats(self):
        """Reset performance tracking"""
        self.parse_count = 0
        self.total_parse_time = 0.0

# Global parser instance
template_parser = TemplateParser()