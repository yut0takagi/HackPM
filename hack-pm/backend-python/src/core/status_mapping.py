"""
Status mapping service for converting template fields to dashboard categories
"""
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from .template_parser import ParsedTemplateData, TemplateType, Priority

logger = logging.getLogger(__name__)

class DashboardStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in-progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

class DashboardCategory(Enum):
    FEATURE = "feature"
    BUG = "bug"
    TASK = "task"
    ENHANCEMENT = "enhancement"
    MAINTENANCE = "maintenance"
    DOCUMENTATION = "documentation"

class DashboardPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class DashboardIssueData:
    """Mapped issue data for dashboard display"""
    status: DashboardStatus
    category: DashboardCategory
    priority: DashboardPriority
    progress_percentage: float
    estimated_hours: Optional[int] = None
    acceptance_criteria_total: int = 0
    acceptance_criteria_completed: int = 0
    has_technical_requirements: bool = False
    is_time_sensitive: bool = False
    branch_linked: bool = False
    pr_linked: bool = False
    # Time-boxed development fields
    hackathon_phase: Optional[str] = None
    deadline_hours_remaining: Optional[float] = None
    is_overdue: bool = False
    priority_escalated: bool = False
    time_box_progress: Optional[float] = None

class StatusMappingService:
    """Service for mapping template data to dashboard status and categories"""
    
    def __init__(self):
        # Label to category mappings
        self.label_category_map = {
            'feature': DashboardCategory.FEATURE,
            'enhancement': DashboardCategory.ENHANCEMENT,
            'new feature': DashboardCategory.FEATURE,
            'bug': DashboardCategory.BUG,
            'bugfix': DashboardCategory.BUG,
            'defect': DashboardCategory.BUG,
            'task': DashboardCategory.TASK,
            'chore': DashboardCategory.MAINTENANCE,
            'maintenance': DashboardCategory.MAINTENANCE,
            'documentation': DashboardCategory.DOCUMENTATION,
            'docs': DashboardCategory.DOCUMENTATION,
        }
        
        # Label to priority mappings
        self.label_priority_map = {
            'critical': DashboardPriority.CRITICAL,
            'urgent': DashboardPriority.CRITICAL,
            'high': DashboardPriority.HIGH,
            'high-priority': DashboardPriority.HIGH,
            'important': DashboardPriority.HIGH,
            'medium': DashboardPriority.MEDIUM,
            'normal': DashboardPriority.MEDIUM,
            'low': DashboardPriority.LOW,
            'minor': DashboardPriority.LOW,
        }
        
        # Status keywords for determining progress
        self.status_keywords = {
            'todo': DashboardStatus.TODO,
            'to do': DashboardStatus.TODO,
            'backlog': DashboardStatus.TODO,
            'open': DashboardStatus.TODO,
            'in progress': DashboardStatus.IN_PROGRESS,
            'in-progress': DashboardStatus.IN_PROGRESS,
            'working': DashboardStatus.IN_PROGRESS,
            'development': DashboardStatus.IN_PROGRESS,
            'review': DashboardStatus.REVIEW,
            'code review': DashboardStatus.REVIEW,
            'testing': DashboardStatus.REVIEW,
            'qa': DashboardStatus.REVIEW,
            'done': DashboardStatus.DONE,
            'completed': DashboardStatus.DONE,
            'closed': DashboardStatus.DONE,
            'resolved': DashboardStatus.DONE,
            'blocked': DashboardStatus.BLOCKED,
            'on hold': DashboardStatus.BLOCKED,
            'waiting': DashboardStatus.BLOCKED,
        }
    
    def map_issue_to_dashboard(
        self, 
        template_data: ParsedTemplateData,
        labels: List[str] = None,
        assignees: List[str] = None,
        issue_state: str = "open",
        has_linked_pr: bool = False,
        has_linked_branch: bool = False,
        timebox_data: Dict[str, Any] = None
    ) -> DashboardIssueData:
        """
        Map parsed template data to dashboard representation
        
        Args:
            template_data: Parsed template data from issue
            labels: GitHub issue labels
            assignees: GitHub issue assignees
            issue_state: GitHub issue state (open/closed)
            has_linked_pr: Whether issue has linked PR
            has_linked_branch: Whether issue has linked branch
            timebox_data: Time-boxed development data from database
            
        Returns:
            DashboardIssueData object for dashboard display
        """
        # Determine category
        category = self._determine_category(template_data, labels)
        
        # Determine priority
        priority = self._determine_priority(template_data, labels)
        
        # Determine status
        status = self._determine_status(
            template_data, labels, assignees, issue_state, 
            has_linked_pr, has_linked_branch
        )
        
        # Calculate progress
        progress_percentage = self._calculate_progress(template_data, status)
        
        # Count acceptance criteria
        ac_total = len(template_data.acceptance_criteria) if template_data.acceptance_criteria else 0
        ac_completed = self._count_completed_acceptance_criteria(template_data.acceptance_criteria)
        
        # Check for technical requirements
        has_tech_req = bool(template_data.technical_requirements)
        
        # Check if time sensitive (has estimated time or urgent priority)
        is_time_sensitive = (
            template_data.estimated_time is not None or 
            priority == DashboardPriority.CRITICAL
        )
        
        # Extract time-boxed development data
        hackathon_phase = None
        deadline_hours_remaining = None
        is_overdue = False
        priority_escalated = False
        time_box_progress = None
        
        if timebox_data:
            hackathon_phase = timebox_data.get('hackathon_phase')
            deadline_hours_remaining = timebox_data.get('hours_until_deadline')
            is_overdue = timebox_data.get('is_overdue', False)
            priority_escalated = timebox_data.get('priority_escalated', False)
            time_box_progress = timebox_data.get('time_remaining_percentage')
            
            # Escalate priority if overdue or time-sensitive
            if is_overdue or (deadline_hours_remaining and deadline_hours_remaining < 2):
                if priority != DashboardPriority.CRITICAL:
                    priority = DashboardPriority.HIGH
                is_time_sensitive = True
        
        return DashboardIssueData(
            status=status,
            category=category,
            priority=priority,
            progress_percentage=progress_percentage,
            estimated_hours=template_data.estimated_time,
            acceptance_criteria_total=ac_total,
            acceptance_criteria_completed=ac_completed,
            has_technical_requirements=has_tech_req,
            is_time_sensitive=is_time_sensitive,
            branch_linked=has_linked_branch,
            pr_linked=has_linked_pr,
            hackathon_phase=hackathon_phase,
            deadline_hours_remaining=deadline_hours_remaining,
            is_overdue=is_overdue,
            priority_escalated=priority_escalated,
            time_box_progress=time_box_progress
        )
    
    def map_pr_to_dashboard(
        self,
        template_data: ParsedTemplateData,
        pr_state: str = "open",
        is_draft: bool = False,
        mergeable: bool = None,
        review_status: str = None
    ) -> DashboardIssueData:
        """
        Map parsed PR template data to dashboard representation
        
        Args:
            template_data: Parsed template data from PR
            pr_state: GitHub PR state (open/closed/merged)
            is_draft: Whether PR is draft
            mergeable: Whether PR is mergeable
            review_status: Review status (approved/changes_requested/etc)
            
        Returns:
            DashboardIssueData object for dashboard display
        """
        # PRs are always categorized as tasks unless specified otherwise
        category = DashboardCategory.TASK
        
        # Determine priority based on breaking changes and related issues
        priority = DashboardPriority.MEDIUM
        if template_data.breaking_changes:
            priority = DashboardPriority.HIGH
        if template_data.related_issues and len(template_data.related_issues) > 3:
            priority = DashboardPriority.HIGH
        
        # Determine status based on PR state and review status
        status = self._determine_pr_status(pr_state, is_draft, review_status, mergeable)
        
        # Calculate progress based on testing checklist
        progress_percentage = self._calculate_pr_progress(template_data, status)
        
        # Count testing checklist items
        testing_total = len(template_data.testing_checklist) if template_data.testing_checklist else 0
        testing_completed = self._count_completed_checklist_items(template_data.testing_checklist)
        
        return DashboardIssueData(
            status=status,
            category=category,
            priority=priority,
            progress_percentage=progress_percentage,
            acceptance_criteria_total=testing_total,
            acceptance_criteria_completed=testing_completed,
            has_technical_requirements=bool(template_data.breaking_changes),
            is_time_sensitive=bool(template_data.breaking_changes),
            branch_linked=True,  # PRs always have branches
            pr_linked=False  # PRs don't link to other PRs
        )
    
    def _determine_category(self, template_data: ParsedTemplateData, labels: List[str] = None) -> DashboardCategory:
        """Determine dashboard category from template data and labels"""
        # First check template type
        if template_data.template_type == TemplateType.FEATURE:
            return DashboardCategory.FEATURE
        elif template_data.template_type == TemplateType.BUG:
            return DashboardCategory.BUG
        elif template_data.template_type == TemplateType.TASK:
            return DashboardCategory.TASK
        
        # Check labels
        if labels:
            for label in labels:
                label_lower = label.lower().strip()
                if label_lower in self.label_category_map:
                    return self.label_category_map[label_lower]
        
        # Default to task
        return DashboardCategory.TASK
    
    def _determine_priority(self, template_data: ParsedTemplateData, labels: List[str] = None) -> DashboardPriority:
        """Determine dashboard priority from template data and labels"""
        # Check labels first (they can override template priority)
        if labels:
            for label in labels:
                label_lower = label.lower().strip()
                if label_lower in self.label_priority_map:
                    return self.label_priority_map[label_lower]
        
        # Then check template priority
        if template_data.priority == Priority.CRITICAL:
            return DashboardPriority.CRITICAL
        elif template_data.priority == Priority.HIGH:
            return DashboardPriority.HIGH
        elif template_data.priority == Priority.MEDIUM:
            return DashboardPriority.MEDIUM
        elif template_data.priority == Priority.LOW:
            return DashboardPriority.LOW
        
        # Default to medium
        return DashboardPriority.MEDIUM
    
    def _determine_status(
        self, 
        template_data: ParsedTemplateData,
        labels: List[str] = None,
        assignees: List[str] = None,
        issue_state: str = "open",
        has_linked_pr: bool = False,
        has_linked_branch: bool = False
    ) -> DashboardStatus:
        """Determine dashboard status from various indicators"""
        # If issue is closed, it's done
        if issue_state == "closed":
            return DashboardStatus.DONE
        
        # Check for status labels
        if labels:
            for label in labels:
                label_lower = label.lower().strip()
                if label_lower in self.status_keywords:
                    return self.status_keywords[label_lower]
        
        # Infer status from other indicators
        if has_linked_pr:
            return DashboardStatus.REVIEW
        elif has_linked_branch or (assignees and len(assignees) > 0):
            return DashboardStatus.IN_PROGRESS
        else:
            return DashboardStatus.TODO
    
    def _determine_pr_status(
        self,
        pr_state: str,
        is_draft: bool,
        review_status: str = None,
        mergeable: bool = None
    ) -> DashboardStatus:
        """Determine PR status from GitHub PR data"""
        if pr_state == "merged":
            return DashboardStatus.DONE
        elif pr_state == "closed":
            return DashboardStatus.DONE
        elif is_draft:
            return DashboardStatus.IN_PROGRESS
        elif review_status == "approved" and mergeable:
            return DashboardStatus.REVIEW
        elif review_status == "changes_requested":
            return DashboardStatus.IN_PROGRESS
        elif mergeable is False:
            return DashboardStatus.BLOCKED
        else:
            return DashboardStatus.REVIEW
    
    def _calculate_progress(self, template_data: ParsedTemplateData, status: DashboardStatus) -> float:
        """Calculate progress percentage based on acceptance criteria and status"""
        # Base progress on status
        status_progress = {
            DashboardStatus.TODO: 0.0,
            DashboardStatus.IN_PROGRESS: 25.0,
            DashboardStatus.REVIEW: 75.0,
            DashboardStatus.DONE: 100.0,
            DashboardStatus.BLOCKED: 10.0,
        }
        
        base_progress = status_progress.get(status, 0.0)
        
        # If we have acceptance criteria, calculate based on completion
        if template_data.acceptance_criteria:
            total_criteria = len(template_data.acceptance_criteria)
            completed_criteria = self._count_completed_acceptance_criteria(template_data.acceptance_criteria)
            
            if total_criteria > 0:
                criteria_progress = (completed_criteria / total_criteria) * 100.0
                # Blend status progress with criteria progress
                return min(100.0, (base_progress + criteria_progress) / 2)
        
        return base_progress
    
    def _calculate_pr_progress(self, template_data: ParsedTemplateData, status: DashboardStatus) -> float:
        """Calculate PR progress based on testing checklist and status"""
        # Base progress on status
        status_progress = {
            DashboardStatus.TODO: 0.0,
            DashboardStatus.IN_PROGRESS: 30.0,
            DashboardStatus.REVIEW: 80.0,
            DashboardStatus.DONE: 100.0,
            DashboardStatus.BLOCKED: 15.0,
        }
        
        base_progress = status_progress.get(status, 0.0)
        
        # If we have testing checklist, calculate based on completion
        if template_data.testing_checklist:
            total_items = len(template_data.testing_checklist)
            completed_items = self._count_completed_checklist_items(template_data.testing_checklist)
            
            if total_items > 0:
                checklist_progress = (completed_items / total_items) * 100.0
                # Blend status progress with checklist progress
                return min(100.0, (base_progress + checklist_progress) / 2)
        
        return base_progress
    
    def _count_completed_acceptance_criteria(self, criteria: List[str] = None) -> int:
        """Count completed acceptance criteria (marked with [x])"""
        if not criteria:
            return 0
        
        completed = 0
        for criterion in criteria:
            # Look for [x] or [X] markers
            if '[x]' in criterion.lower() or '✓' in criterion or '✔' in criterion:
                completed += 1
        
        return completed
    
    def _count_completed_checklist_items(self, checklist: List[str] = None) -> int:
        """Count completed checklist items (marked with [x])"""
        if not checklist:
            return 0
        
        completed = 0
        for item in checklist:
            # Look for [x] or [X] markers (case insensitive)
            item_lower = item.lower()
            if '[x]' in item_lower or '✓' in item or '✔' in item:
                completed += 1
        
        return completed
    
    def get_category_stats(self, issues_data: List[DashboardIssueData]) -> Dict[str, Dict[str, int]]:
        """Get statistics by category"""
        stats = {}
        
        for issue in issues_data:
            category = issue.category.value
            if category not in stats:
                stats[category] = {
                    'total': 0,
                    'todo': 0,
                    'in-progress': 0,
                    'review': 0,
                    'done': 0,
                    'blocked': 0
                }
            
            stats[category]['total'] += 1
            status_key = issue.status.value
            if status_key in stats[category]:
                stats[category][status_key] += 1
        
        return stats
    
    def get_priority_distribution(self, issues_data: List[DashboardIssueData]) -> Dict[str, int]:
        """Get priority distribution"""
        distribution = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        for issue in issues_data:
            distribution[issue.priority.value] += 1
        
        return distribution
    
    def get_time_sensitive_stats(self, issues_data: List[DashboardIssueData]) -> Dict[str, Any]:
        """Get time-sensitive issue statistics for hackathon optimization"""
        stats = {
            'total_time_sensitive': 0,
            'overdue_count': 0,
            'escalated_count': 0,
            'by_phase': {
                'planning': 0,
                'development': 0,
                'testing': 0,
                'presentation': 0
            },
            'urgent_next_6_hours': 0,
            'urgent_next_24_hours': 0,
            'average_time_remaining': 0
        }
        
        time_remaining_values = []
        
        for issue in issues_data:
            if issue.is_time_sensitive:
                stats['total_time_sensitive'] += 1
            
            if issue.is_overdue:
                stats['overdue_count'] += 1
            
            if issue.priority_escalated:
                stats['escalated_count'] += 1
            
            if issue.hackathon_phase:
                phase = issue.hackathon_phase
                if phase in stats['by_phase']:
                    stats['by_phase'][phase] += 1
            
            if issue.deadline_hours_remaining is not None:
                hours = issue.deadline_hours_remaining
                time_remaining_values.append(hours)
                
                if 0 < hours <= 6:
                    stats['urgent_next_6_hours'] += 1
                elif 0 < hours <= 24:
                    stats['urgent_next_24_hours'] += 1
        
        # Calculate average time remaining
        if time_remaining_values:
            stats['average_time_remaining'] = sum(time_remaining_values) / len(time_remaining_values)
        
        return stats
    
    def optimize_for_hackathon_dashboard(self, issues_data: List[DashboardIssueData]) -> Dict[str, Any]:
        """Optimize issue data for hackathon dashboard display"""
        # Sort by urgency and priority
        sorted_issues = sorted(issues_data, key=lambda x: (
            x.is_overdue,  # Overdue first
            x.priority_escalated,  # Then escalated
            x.deadline_hours_remaining or float('inf'),  # Then by deadline
            x.priority.value == 'critical',  # Then critical priority
            x.priority.value == 'high'  # Then high priority
        ), reverse=True)
        
        # Group by hackathon phase
        by_phase = {}
        for issue in sorted_issues:
            phase = issue.hackathon_phase or 'unassigned'
            if phase not in by_phase:
                by_phase[phase] = []
            by_phase[phase].append(issue)
        
        # Get quick stats
        quick_stats = self.get_time_sensitive_stats(issues_data)
        
        return {
            'sorted_issues': sorted_issues[:20],  # Top 20 most urgent
            'by_phase': by_phase,
            'quick_stats': quick_stats,
            'cache_timestamp': datetime.utcnow().isoformat()
        }

# Global service instance
status_mapping_service = StatusMappingService()