"""
Time-boxed development service for hackathon optimization
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import json

from .database import Issue, HackathonTimeBox, Repository
from ..core.template_parser import ParsedTemplateData, Priority

class TimeBoxService:
    """Service for managing time-boxed development features"""
    
    def __init__(self):
        self.hackathon_phases = {
            'planning': {'duration_hours': 4, 'priority_multiplier': 1.0},
            'development': {'duration_hours': 20, 'priority_multiplier': 1.2},
            'testing': {'duration_hours': 6, 'priority_multiplier': 1.5},
            'presentation': {'duration_hours': 2, 'priority_multiplier': 2.0}
        }
    
    def create_time_box(self, db: Session, repo_id: int, name: str, phase: str, 
                       start_time: datetime, duration_hours: int, description: str = None) -> HackathonTimeBox:
        """Create a new time box for hackathon development"""
        end_time = start_time + timedelta(hours=duration_hours)
        
        # Deactivate other active time boxes for this repo
        db.query(HackathonTimeBox).filter(
            and_(HackathonTimeBox.repo_id == repo_id, HackathonTimeBox.is_active == True)
        ).update({'is_active': False})
        
        time_box = HackathonTimeBox(
            repo_id=repo_id,
            name=name,
            phase=phase,
            start_time=start_time,
            end_time=end_time,
            description=description,
            is_active=True
        )
        
        db.add(time_box)
        db.commit()
        db.refresh(time_box)
        
        return time_box
    
    def get_active_time_box(self, db: Session, repo_id: int) -> Optional[HackathonTimeBox]:
        """Get the currently active time box for a repository"""
        return db.query(HackathonTimeBox).filter(
            and_(
                HackathonTimeBox.repo_id == repo_id,
                HackathonTimeBox.is_active == True
            )
        ).first()
    
    def get_time_boxes(self, db: Session, repo_id: int) -> List[HackathonTimeBox]:
        """Get all time boxes for a repository"""
        return db.query(HackathonTimeBox).filter(
            HackathonTimeBox.repo_id == repo_id
        ).order_by(desc(HackathonTimeBox.created_at)).all()
    
    def set_issue_deadline(self, db: Session, issue_id: int, deadline: datetime, 
                          estimated_hours: int = None) -> Issue:
        """Set deadline and time box for an issue"""
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise ValueError(f"Issue {issue_id} not found")
        
        issue.deadline = deadline
        if estimated_hours:
            issue.estimated_hours = estimated_hours
        
        # Set time box start if not already set
        if not issue.time_box_start:
            issue.time_box_start = datetime.utcnow()
        
        # Calculate time box end based on estimated hours or deadline
        if estimated_hours:
            issue.time_box_end = issue.time_box_start + timedelta(hours=estimated_hours)
        else:
            issue.time_box_end = deadline
        
        db.commit()
        db.refresh(issue)
        
        return issue
    
    def start_issue_work(self, db: Session, issue_id: int) -> Issue:
        """Mark an issue as started and begin time tracking"""
        issue = db.query(Issue).filter(Issue.id == issue_id).first()
        if not issue:
            raise ValueError(f"Issue {issue_id} not found")
        
        if not issue.time_box_start:
            issue.time_box_start = datetime.utcnow()
            
            # Set time box end based on estimated hours or default
            hours = issue.estimated_hours or 4  # Default 4 hours
            issue.time_box_end = issue.time_box_start + timedelta(hours=hours)
            
            db.commit()
            db.refresh(issue)
        
        return issue
    
    def get_time_sensitive_issues(self, db: Session, repo_id: int, 
                                 hours_threshold: int = 24) -> List[Issue]:
        """Get issues that are approaching their deadlines"""
        threshold_time = datetime.utcnow() + timedelta(hours=hours_threshold)
        
        return db.query(Issue).filter(
            and_(
                Issue.repo_id == repo_id,
                Issue.state == 'open',
                Issue.deadline.isnot(None),
                Issue.deadline <= threshold_time
            )
        ).order_by(Issue.deadline).all()
    
    def escalate_overdue_issues(self, db: Session, repo_id: int) -> List[Issue]:
        """Automatically escalate issues that are past their deadlines"""
        now = datetime.utcnow()
        overdue_issues = db.query(Issue).filter(
            and_(
                Issue.repo_id == repo_id,
                Issue.state == 'open',
                Issue.deadline.isnot(None),
                Issue.deadline < now,
                Issue.priority_escalated == False
            )
        ).all()
        
        escalated = []
        for issue in overdue_issues:
            issue.priority_escalated = True
            escalated.append(issue)
        
        if escalated:
            db.commit()
        
        return escalated
    
    def get_time_box_statistics(self, db: Session, repo_id: int) -> Dict[str, Any]:
        """Get statistics for time-boxed development"""
        active_time_box = self.get_active_time_box(db, repo_id)
        
        # Get issues with time tracking
        time_tracked_issues = db.query(Issue).filter(
            and_(
                Issue.repo_id == repo_id,
                Issue.time_box_start.isnot(None)
            )
        ).all()
        
        # Calculate statistics
        total_estimated_hours = sum(issue.estimated_hours or 0 for issue in time_tracked_issues)
        completed_issues = [issue for issue in time_tracked_issues if issue.state == 'closed']
        completed_hours = sum(issue.estimated_hours or 0 for issue in completed_issues)
        
        # Time-sensitive issues
        time_sensitive = self.get_time_sensitive_issues(db, repo_id, 6)  # Next 6 hours
        overdue = self.get_time_sensitive_issues(db, repo_id, 0)  # Already overdue
        
        stats = {
            'active_time_box': {
                'name': active_time_box.name if active_time_box else None,
                'phase': active_time_box.phase if active_time_box else None,
                'start_time': active_time_box.start_time.isoformat() if active_time_box else None,
                'end_time': active_time_box.end_time.isoformat() if active_time_box else None,
                'remaining_hours': self._calculate_remaining_hours(active_time_box) if active_time_box else None
            },
            'time_tracking': {
                'total_issues': len(time_tracked_issues),
                'completed_issues': len(completed_issues),
                'total_estimated_hours': total_estimated_hours,
                'completed_hours': completed_hours,
                'completion_rate': (completed_hours / total_estimated_hours * 100) if total_estimated_hours > 0 else 0
            },
            'urgency': {
                'time_sensitive_count': len(time_sensitive),
                'overdue_count': len(overdue),
                'escalated_count': len([issue for issue in time_tracked_issues if issue.priority_escalated])
            }
        }
        
        return stats
    
    def _calculate_remaining_hours(self, time_box: HackathonTimeBox) -> float:
        """Calculate remaining hours in a time box"""
        if not time_box:
            return 0
        
        now = datetime.utcnow()
        if now >= time_box.end_time:
            return 0
        
        remaining = time_box.end_time - now
        return remaining.total_seconds() / 3600
    
    def get_phase_recommendations(self, db: Session, repo_id: int) -> Dict[str, Any]:
        """Get recommendations for hackathon phase transitions"""
        active_time_box = self.get_active_time_box(db, repo_id)
        
        if not active_time_box:
            return {
                'current_phase': None,
                'recommended_action': 'create_planning_phase',
                'message': 'Start hackathon with a planning phase'
            }
        
        remaining_hours = self._calculate_remaining_hours(active_time_box)
        current_phase = active_time_box.phase
        
        # Get issue statistics for current phase
        open_issues = db.query(Issue).filter(
            and_(
                Issue.repo_id == repo_id,
                Issue.state == 'open',
                Issue.hackathon_phase == current_phase
            )
        ).count()
        
        recommendations = {
            'current_phase': current_phase,
            'remaining_hours': remaining_hours,
            'open_issues': open_issues
        }
        
        # Phase-specific recommendations
        if current_phase == 'planning':
            if remaining_hours < 1 or open_issues == 0:
                recommendations.update({
                    'recommended_action': 'transition_to_development',
                    'message': 'Planning complete. Ready to start development phase.'
                })
            else:
                recommendations.update({
                    'recommended_action': 'continue_planning',
                    'message': f'{remaining_hours:.1f} hours remaining for planning. Focus on issue creation.'
                })
        
        elif current_phase == 'development':
            if remaining_hours < 2:
                recommendations.update({
                    'recommended_action': 'transition_to_testing',
                    'message': 'Development time running low. Consider moving to testing phase.'
                })
            else:
                recommendations.update({
                    'recommended_action': 'continue_development',
                    'message': f'{remaining_hours:.1f} hours remaining for development. {open_issues} issues still open.'
                })
        
        elif current_phase == 'testing':
            if remaining_hours < 1:
                recommendations.update({
                    'recommended_action': 'transition_to_presentation',
                    'message': 'Testing time complete. Prepare for presentation.'
                })
            else:
                recommendations.update({
                    'recommended_action': 'continue_testing',
                    'message': f'{remaining_hours:.1f} hours remaining for testing.'
                })
        
        elif current_phase == 'presentation':
            recommendations.update({
                'recommended_action': 'finalize_presentation',
                'message': f'{remaining_hours:.1f} hours remaining for presentation preparation.'
            })
        
        return recommendations
    
    def create_rapid_issue(self, db: Session, repo_id: int, title: str, 
                          issue_type: str = 'task', priority: str = 'medium',
                          estimated_hours: int = 2) -> Dict[str, Any]:
        """Create a rapid issue template for hackathon development"""
        active_time_box = self.get_active_time_box(db, repo_id)
        current_phase = active_time_box.phase if active_time_box else 'development'
        
        # Generate simplified issue body based on type
        if issue_type == 'feature':
            body = f"""## Feature Request

**User Story:** As a user, I want {title.lower()}, so that I can achieve my goals.

**Acceptance Criteria:**
- [ ] Basic functionality implemented
- [ ] User interface created
- [ ] Basic testing completed

**Estimated Time:** {estimated_hours} hours
**Priority:** {priority}
**Phase:** {current_phase}
"""
        elif issue_type == 'bug':
            body = f"""## Bug Report

**Description:** {title}

**Steps to Reproduce:**
1. [Add steps here]

**Expected Behavior:** [Describe expected behavior]
**Actual Behavior:** [Describe actual behavior]

**Priority:** {priority}
**Estimated Fix Time:** {estimated_hours} hours
"""
        else:  # task
            body = f"""## Task

**Description:** {title}

**Checklist:**
- [ ] Task implementation
- [ ] Testing
- [ ] Documentation

**Estimated Time:** {estimated_hours} hours
**Priority:** {priority}
**Phase:** {current_phase}
"""
        
        # Calculate deadline based on current time box
        deadline = None
        if active_time_box:
            deadline = min(
                datetime.utcnow() + timedelta(hours=estimated_hours),
                active_time_box.end_time
            )
        
        return {
            'title': title,
            'body': body,
            'labels': [issue_type, priority, f'phase:{current_phase}'],
            'estimated_hours': estimated_hours,
            'deadline': deadline.isoformat() if deadline else None,
            'hackathon_phase': current_phase
        }

# Global service instance
timebox_service = TimeBoxService()