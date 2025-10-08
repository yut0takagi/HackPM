"""
Branch naming convention system for GitHub integration
"""
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session
from src.services.database import Branch, Issue, Repository

logger = logging.getLogger(__name__)

class BranchType(Enum):
    FEATURE = "feature"
    BUGFIX = "bugfix"
    HOTFIX = "hotfix"
    RELEASE = "release"
    CHORE = "chore"
    UNKNOWN = "unknown"

@dataclass
class BranchInfo:
    """Parsed branch information"""
    branch_type: BranchType
    issue_number: Optional[int] = None
    description: Optional[str] = None
    is_valid: bool = True
    validation_errors: List[str] = None

@dataclass
class BranchIssueLink:
    """Link between branch and issue"""
    branch_id: int
    branch_name: str
    issue_id: Optional[int] = None
    issue_number: Optional[int] = None
    confidence_score: float = 0.0
    link_type: str = "automatic"  # automatic, manual, suggested

class BranchNamingService:
    """Service for branch naming convention validation and issue linking"""
    
    def __init__(self):
        # Branch naming patterns
        self.branch_patterns = {
            BranchType.FEATURE: [
                r'^feature/(\d+)-(.+)$',
                r'^feat/(\d+)-(.+)$',
                r'^feature-(\d+)-(.+)$',
                r'^(\d+)-feature-(.+)$',
            ],
            BranchType.BUGFIX: [
                r'^bugfix/(\d+)-(.+)$',
                r'^bug/(\d+)-(.+)$',
                r'^fix/(\d+)-(.+)$',
                r'^bugfix-(\d+)-(.+)$',
                r'^(\d+)-bugfix-(.+)$',
            ],
            BranchType.HOTFIX: [
                r'^hotfix/(\d+)-(.+)$',
                r'^hotfix-(\d+)-(.+)$',
                r'^(\d+)-hotfix-(.+)$',
            ],
            BranchType.RELEASE: [
                r'^release/(.+)$',
                r'^release-(.+)$',
            ],
            BranchType.CHORE: [
                r'^chore/(\d+)-(.+)$',
                r'^chore-(\d+)-(.+)$',
                r'^(\d+)-chore-(.+)$',
            ]
        }
        
        # Fallback patterns for issue number extraction
        self.issue_number_patterns = [
            r'(\d+)',  # Any number in branch name
            r'#(\d+)',  # Hash followed by number
            r'issue-(\d+)',  # issue- prefix
            r'task-(\d+)',  # task- prefix
        ]
        
        # Description validation rules
        self.description_rules = {
            'min_length': 3,
            'max_length': 50,
            'allowed_chars': r'^[a-zA-Z0-9\-_]+$',
            'no_consecutive_hyphens': True,
            'no_leading_trailing_hyphens': True,
        }
    
    def parse_branch_name(self, branch_name: str) -> BranchInfo:
        """
        Parse branch name to extract type, issue number, and description
        
        Args:
            branch_name: The branch name to parse
            
        Returns:
            BranchInfo object with parsed information
        """
        if not branch_name:
            return BranchInfo(
                branch_type=BranchType.UNKNOWN,
                is_valid=False,
                validation_errors=["Branch name is empty"]
            )
        
        # Try to match against known patterns
        for branch_type, patterns in self.branch_patterns.items():
            for pattern in patterns:
                match = re.match(pattern, branch_name, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    
                    # Extract issue number and description based on pattern
                    if branch_type == BranchType.RELEASE:
                        # Release branches don't have issue numbers
                        return BranchInfo(
                            branch_type=branch_type,
                            description=groups[0] if groups else None,
                            is_valid=True
                        )
                    else:
                        # Other branches should have issue number and description
                        issue_number = None
                        description = None
                        
                        if len(groups) >= 2:
                            try:
                                issue_number = int(groups[0])
                                description = groups[1]
                            except (ValueError, IndexError):
                                try:
                                    issue_number = int(groups[1])
                                    description = groups[0]
                                except (ValueError, IndexError):
                                    pass
                        
                        # Validate description
                        validation_errors = self._validate_description(description)
                        
                        return BranchInfo(
                            branch_type=branch_type,
                            issue_number=issue_number,
                            description=description,
                            is_valid=len(validation_errors) == 0,
                            validation_errors=validation_errors
                        )
        
        # If no pattern matches, try to extract issue number anyway
        issue_number = self._extract_issue_number(branch_name)
        
        # Determine branch type from name
        branch_type = self._infer_branch_type(branch_name)
        
        return BranchInfo(
            branch_type=branch_type,
            issue_number=issue_number,
            description=branch_name,
            is_valid=False,
            validation_errors=["Branch name doesn't follow naming convention"]
        )
    
    def validate_branch_name(self, branch_name: str, branch_type: BranchType = None) -> Tuple[bool, List[str]]:
        """
        Validate branch name against naming conventions
        
        Args:
            branch_name: The branch name to validate
            branch_type: Expected branch type (optional)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        branch_info = self.parse_branch_name(branch_name)
        
        errors = []
        
        # Check if branch type matches expected
        if branch_type and branch_info.branch_type != branch_type:
            errors.append(f"Expected {branch_type.value} branch, got {branch_info.branch_type.value}")
        
        # Add parsing errors
        if branch_info.validation_errors:
            errors.extend(branch_info.validation_errors)
        
        return len(errors) == 0, errors
    
    def suggest_branch_name(self, issue_number: int, issue_title: str, branch_type: BranchType = BranchType.FEATURE) -> str:
        """
        Suggest a branch name based on issue information
        
        Args:
            issue_number: GitHub issue number
            issue_title: GitHub issue title
            branch_type: Type of branch to create
            
        Returns:
            Suggested branch name
        """
        # Clean and format the description
        description = self._format_description(issue_title)
        
        # Generate branch name based on type
        if branch_type == BranchType.FEATURE:
            return f"feature/{issue_number}-{description}"
        elif branch_type == BranchType.BUGFIX:
            return f"bugfix/{issue_number}-{description}"
        elif branch_type == BranchType.HOTFIX:
            return f"hotfix/{issue_number}-{description}"
        elif branch_type == BranchType.CHORE:
            return f"chore/{issue_number}-{description}"
        else:
            return f"{branch_type.value}/{issue_number}-{description}"
    
    def link_branches_to_issues(self, db: Session, repo_id: int) -> List[BranchIssueLink]:
        """
        Automatically link branches to issues based on naming conventions
        
        Args:
            db: Database session
            repo_id: Repository ID
            
        Returns:
            List of branch-issue links created
        """
        links = []
        
        # Get all branches for the repository
        branches = db.query(Branch).filter(Branch.repo_id == repo_id).all()
        
        # Get all issues for the repository
        issues = db.query(Issue).filter(Issue.repo_id == repo_id).all()
        issue_map = {issue.number: issue for issue in issues}
        
        for branch in branches:
            # Skip default branches
            if branch.is_default:
                continue
            
            # Parse branch name
            branch_info = self.parse_branch_name(branch.name)
            
            # Try to link to issue
            link = self._create_branch_issue_link(branch, branch_info, issue_map)
            if link:
                links.append(link)
        
        return links
    
    def find_related_branches(self, db: Session, issue_number: int, repo_id: int) -> List[Branch]:
        """
        Find branches related to a specific issue
        
        Args:
            db: Database session
            issue_number: GitHub issue number
            repo_id: Repository ID
            
        Returns:
            List of related branches
        """
        related_branches = []
        
        # Get all branches for the repository
        branches = db.query(Branch).filter(Branch.repo_id == repo_id).all()
        
        for branch in branches:
            # Skip default branches
            if branch.is_default:
                continue
            
            # Parse branch name
            branch_info = self.parse_branch_name(branch.name)
            
            # Check if branch is related to the issue
            if branch_info.issue_number == issue_number:
                related_branches.append(branch)
            elif str(issue_number) in branch.name:
                # Fallback: check if issue number appears anywhere in branch name
                related_branches.append(branch)
        
        return related_branches
    
    def _extract_issue_number(self, branch_name: str) -> Optional[int]:
        """Extract issue number from branch name using fallback patterns"""
        for pattern in self.issue_number_patterns:
            match = re.search(pattern, branch_name)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    def _infer_branch_type(self, branch_name: str) -> BranchType:
        """Infer branch type from branch name"""
        name_lower = branch_name.lower()
        
        # Check more specific patterns first
        if 'hotfix' in name_lower:
            return BranchType.HOTFIX
        elif any(keyword in name_lower for keyword in ['feature', 'feat']):
            return BranchType.FEATURE
        elif any(keyword in name_lower for keyword in ['bug', 'fix', 'bugfix']):
            return BranchType.BUGFIX
        elif 'release' in name_lower:
            return BranchType.RELEASE
        elif 'chore' in name_lower:
            return BranchType.CHORE
        else:
            return BranchType.UNKNOWN
    
    def _validate_description(self, description: str) -> List[str]:
        """Validate branch description against rules"""
        if not description:
            return ["Description is required"]
        
        errors = []
        
        # Check length
        if len(description) < self.description_rules['min_length']:
            errors.append(f"Description too short (minimum {self.description_rules['min_length']} characters)")
        
        if len(description) > self.description_rules['max_length']:
            errors.append(f"Description too long (maximum {self.description_rules['max_length']} characters)")
        
        # Check allowed characters
        if not re.match(self.description_rules['allowed_chars'], description):
            errors.append("Description contains invalid characters (only letters, numbers, hyphens, and underscores allowed)")
        
        # Check consecutive hyphens
        if self.description_rules['no_consecutive_hyphens'] and '--' in description:
            errors.append("Description cannot contain consecutive hyphens")
        
        # Check leading/trailing hyphens
        if self.description_rules['no_leading_trailing_hyphens']:
            if description.startswith('-') or description.endswith('-'):
                errors.append("Description cannot start or end with hyphens")
        
        return errors
    
    def _format_description(self, title: str) -> str:
        """Format issue title into a valid branch description"""
        if not title:
            return "untitled"
        
        # Convert to lowercase and replace spaces with hyphens
        description = title.lower()
        description = re.sub(r'[^\w\s-]', '', description)  # Remove special chars
        description = re.sub(r'\s+', '-', description)  # Replace spaces with hyphens
        description = re.sub(r'-+', '-', description)  # Remove consecutive hyphens
        description = description.strip('-')  # Remove leading/trailing hyphens
        
        # Truncate if too long
        max_length = self.description_rules['max_length']
        if len(description) > max_length:
            description = description[:max_length].rstrip('-')
        
        return description or "untitled"
    
    def _create_branch_issue_link(
        self, 
        branch: Branch, 
        branch_info: BranchInfo, 
        issue_map: Dict[int, Issue]
    ) -> Optional[BranchIssueLink]:
        """Create a branch-issue link if possible"""
        if not branch_info.issue_number:
            return None
        
        issue = issue_map.get(branch_info.issue_number)
        if not issue:
            return None
        
        # Calculate confidence score
        confidence = 1.0 if branch_info.is_valid else 0.7
        
        return BranchIssueLink(
            branch_id=branch.id,
            branch_name=branch.name,
            issue_id=issue.id,
            issue_number=issue.number,
            confidence_score=confidence,
            link_type="automatic"
        )
    
    def get_naming_convention_stats(self, db: Session, repo_id: int) -> Dict[str, Any]:
        """Get statistics about branch naming convention compliance"""
        branches = db.query(Branch).filter(Branch.repo_id == repo_id).all()
        
        stats = {
            'total_branches': len(branches),
            'compliant_branches': 0,
            'non_compliant_branches': 0,
            'branch_types': {bt.value: 0 for bt in BranchType},
            'linked_to_issues': 0,
            'compliance_percentage': 0.0
        }
        
        for branch in branches:
            if branch.is_default:
                continue
            
            branch_info = self.parse_branch_name(branch.name)
            
            if branch_info.is_valid:
                stats['compliant_branches'] += 1
            else:
                stats['non_compliant_branches'] += 1
            
            stats['branch_types'][branch_info.branch_type.value] += 1
            
            if branch_info.issue_number:
                stats['linked_to_issues'] += 1
        
        # Calculate compliance percentage
        total_non_default = stats['total_branches'] - stats['branch_types']['unknown']
        if total_non_default > 0:
            stats['compliance_percentage'] = (stats['compliant_branches'] / total_non_default) * 100
        
        return stats

# Global service instance
branch_naming_service = BranchNamingService()