"""
Core logic modules for GitHub template processing
"""
from .template_parser import TemplateParser, template_parser, TemplateType, Priority, ParsedTemplateData
from .branch_naming import BranchNamingService, branch_naming_service, BranchType, BranchInfo
from .status_mapping import StatusMappingService, status_mapping_service, DashboardStatus, DashboardCategory, DashboardPriority

__all__ = [
    'TemplateParser', 'template_parser', 'TemplateType', 'Priority', 'ParsedTemplateData',
    'BranchNamingService', 'branch_naming_service', 'BranchType', 'BranchInfo',
    'StatusMappingService', 'status_mapping_service', 'DashboardStatus', 'DashboardCategory', 'DashboardPriority'
]