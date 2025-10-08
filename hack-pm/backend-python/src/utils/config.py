#!/usr/bin/env python3
"""
Configuration management for GitHub template system
Centralized configuration with environment variable support
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ParsingConfig:
    """Configuration for template parsing"""
    max_text_length: int = 10000
    max_list_items: int = 100
    enable_caching: bool = True
    strict_yaml_parsing: bool = False
    sanitization_enabled: bool = True
    performance_tracking: bool = True
    
    # Security settings
    allow_html_tags: bool = False
    allow_javascript: bool = False
    max_nesting_depth: int = 10
    
    # Performance settings
    cache_size: int = 128
    timeout_seconds: float = 30.0
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if self.max_text_length <= 0:
            raise ValueError("max_text_length must be positive")
        if self.max_list_items <= 0:
            raise ValueError("max_list_items must be positive")
        if self.cache_size <= 0:
            raise ValueError("cache_size must be positive")

@dataclass
class StatusMappingConfig:
    """Configuration for status mapping"""
    enable_time_boxing: bool = True
    enable_hackathon_features: bool = True
    default_priority: str = "medium"
    escalation_threshold_hours: float = 2.0
    
    # Priority escalation rules
    escalate_overdue: bool = True
    escalate_critical_bugs: bool = True
    escalate_breaking_changes: bool = True
    
    # Dashboard optimization
    max_dashboard_items: int = 1000
    cache_dashboard_seconds: int = 300
    
    def __post_init__(self):
        """Validate configuration"""
        valid_priorities = ["critical", "high", "medium", "low"]
        if self.default_priority not in valid_priorities:
            raise ValueError(f"default_priority must be one of {valid_priorities}")

@dataclass
class BranchNamingConfig:
    """Configuration for branch naming"""
    enforce_naming_convention: bool = True
    allow_custom_patterns: bool = False
    max_description_length: int = 50
    min_description_length: int = 3
    
    # Allowed branch prefixes
    allowed_prefixes: List[str] = field(default_factory=lambda: [
        "feature", "feat", "bugfix", "bug", "fix", 
        "hotfix", "chore", "release", "docs"
    ])
    
    # Validation rules
    require_issue_number: bool = True
    allow_special_chars: bool = False
    case_sensitive: bool = False
    
    def __post_init__(self):
        """Validate configuration"""
        if self.max_description_length <= self.min_description_length:
            raise ValueError("max_description_length must be greater than min_description_length")

@dataclass
class TestingConfig:
    """Configuration for testing"""
    enable_performance_tests: bool = True
    enable_security_tests: bool = True
    enable_integration_tests: bool = True
    
    # Performance thresholds
    max_parse_time_ms: float = 100.0
    max_mapping_time_ms: float = 10.0
    max_validation_time_ms: float = 5.0
    
    # Test data generation
    generate_large_datasets: bool = False
    max_test_iterations: int = 1000
    
    # Mock data settings
    mock_api_delay_ms: float = 10.0
    mock_failure_rate: float = 0.05

@dataclass
class SystemConfig:
    """Main system configuration"""
    parsing: ParsingConfig = field(default_factory=ParsingConfig)
    status_mapping: StatusMappingConfig = field(default_factory=StatusMappingConfig)
    branch_naming: BranchNamingConfig = field(default_factory=BranchNamingConfig)
    testing: TestingConfig = field(default_factory=TestingConfig)
    
    # Global settings
    debug_mode: bool = False
    log_level: str = "INFO"
    environment: str = "development"
    
    def __post_init__(self):
        """Validate global configuration"""
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(f"log_level must be one of {valid_log_levels}")
        
        valid_environments = ["development", "testing", "staging", "production"]
        if self.environment not in valid_environments:
            raise ValueError(f"environment must be one of {valid_environments}")

class ConfigManager:
    """Manages configuration loading and environment variable integration"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._find_config_file()
        self._config: Optional[SystemConfig] = None
        
    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations"""
        possible_locations = [
            "config.json",
            "config/config.json",
            ".config/github-templates.json",
            os.path.expanduser("~/.config/github-templates.json"),
        ]
        
        for location in possible_locations:
            if os.path.exists(location):
                return location
        
        return None
    
    def load_config(self) -> SystemConfig:
        """Load configuration from file and environment variables"""
        if self._config is not None:
            return self._config
        
        # Start with default configuration
        config_dict = {}
        
        # Load from file if available
        if self.config_file and os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    config_dict.update(file_config)
                logger.info(f"Loaded configuration from {self.config_file}")
            except Exception as e:
                logger.warning(f"Failed to load config file {self.config_file}: {e}")
        
        # Override with environment variables
        env_overrides = self._load_from_environment()
        config_dict = self._merge_configs(config_dict, env_overrides)
        
        # Create configuration objects
        self._config = self._create_config_from_dict(config_dict)
        
        return self._config
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        env_config = {}
        
        # Parsing configuration
        parsing_config = {}
        if os.getenv('TEMPLATE_MAX_TEXT_LENGTH'):
            parsing_config['max_text_length'] = int(os.getenv('TEMPLATE_MAX_TEXT_LENGTH'))
        if os.getenv('TEMPLATE_MAX_LIST_ITEMS'):
            parsing_config['max_list_items'] = int(os.getenv('TEMPLATE_MAX_LIST_ITEMS'))
        if os.getenv('TEMPLATE_ENABLE_CACHING'):
            parsing_config['enable_caching'] = os.getenv('TEMPLATE_ENABLE_CACHING').lower() == 'true'
        if os.getenv('TEMPLATE_STRICT_YAML'):
            parsing_config['strict_yaml_parsing'] = os.getenv('TEMPLATE_STRICT_YAML').lower() == 'true'
        if os.getenv('TEMPLATE_SANITIZATION'):
            parsing_config['sanitization_enabled'] = os.getenv('TEMPLATE_SANITIZATION').lower() == 'true'
        
        if parsing_config:
            env_config['parsing'] = parsing_config
        
        # Status mapping configuration
        status_config = {}
        if os.getenv('STATUS_ENABLE_TIME_BOXING'):
            status_config['enable_time_boxing'] = os.getenv('STATUS_ENABLE_TIME_BOXING').lower() == 'true'
        if os.getenv('STATUS_ENABLE_HACKATHON'):
            status_config['enable_hackathon_features'] = os.getenv('STATUS_ENABLE_HACKATHON').lower() == 'true'
        if os.getenv('STATUS_DEFAULT_PRIORITY'):
            status_config['default_priority'] = os.getenv('STATUS_DEFAULT_PRIORITY').lower()
        if os.getenv('STATUS_ESCALATION_THRESHOLD'):
            status_config['escalation_threshold_hours'] = float(os.getenv('STATUS_ESCALATION_THRESHOLD'))
        
        if status_config:
            env_config['status_mapping'] = status_config
        
        # Branch naming configuration
        branch_config = {}
        if os.getenv('BRANCH_ENFORCE_CONVENTION'):
            branch_config['enforce_naming_convention'] = os.getenv('BRANCH_ENFORCE_CONVENTION').lower() == 'true'
        if os.getenv('BRANCH_MAX_DESC_LENGTH'):
            branch_config['max_description_length'] = int(os.getenv('BRANCH_MAX_DESC_LENGTH'))
        if os.getenv('BRANCH_MIN_DESC_LENGTH'):
            branch_config['min_description_length'] = int(os.getenv('BRANCH_MIN_DESC_LENGTH'))
        if os.getenv('BRANCH_REQUIRE_ISSUE_NUMBER'):
            branch_config['require_issue_number'] = os.getenv('BRANCH_REQUIRE_ISSUE_NUMBER').lower() == 'true'
        
        if branch_config:
            env_config['branch_naming'] = branch_config
        
        # Global settings
        if os.getenv('DEBUG_MODE'):
            env_config['debug_mode'] = os.getenv('DEBUG_MODE').lower() == 'true'
        if os.getenv('LOG_LEVEL'):
            env_config['log_level'] = os.getenv('LOG_LEVEL').upper()
        if os.getenv('ENVIRONMENT'):
            env_config['environment'] = os.getenv('ENVIRONMENT').lower()
        
        return env_config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _create_config_from_dict(self, config_dict: Dict[str, Any]) -> SystemConfig:
        """Create SystemConfig from dictionary"""
        # Extract sub-configurations
        parsing_dict = config_dict.get('parsing', {})
        status_dict = config_dict.get('status_mapping', {})
        branch_dict = config_dict.get('branch_naming', {})
        testing_dict = config_dict.get('testing', {})
        
        # Create sub-configuration objects
        parsing_config = ParsingConfig(**parsing_dict)
        status_config = StatusMappingConfig(**status_dict)
        branch_config = BranchNamingConfig(**branch_dict)
        testing_config = TestingConfig(**testing_dict)
        
        # Create main configuration
        main_config_dict = {k: v for k, v in config_dict.items() 
                           if k not in ['parsing', 'status_mapping', 'branch_naming', 'testing']}
        
        return SystemConfig(
            parsing=parsing_config,
            status_mapping=status_config,
            branch_naming=branch_config,
            testing=testing_config,
            **main_config_dict
        )
    
    def save_config(self, config: SystemConfig, file_path: Optional[str] = None):
        """Save configuration to file"""
        file_path = file_path or self.config_file or "config.json"
        
        # Convert to dictionary
        config_dict = {
            'parsing': {
                'max_text_length': config.parsing.max_text_length,
                'max_list_items': config.parsing.max_list_items,
                'enable_caching': config.parsing.enable_caching,
                'strict_yaml_parsing': config.parsing.strict_yaml_parsing,
                'sanitization_enabled': config.parsing.sanitization_enabled,
                'performance_tracking': config.parsing.performance_tracking,
                'allow_html_tags': config.parsing.allow_html_tags,
                'allow_javascript': config.parsing.allow_javascript,
                'max_nesting_depth': config.parsing.max_nesting_depth,
                'cache_size': config.parsing.cache_size,
                'timeout_seconds': config.parsing.timeout_seconds,
            },
            'status_mapping': {
                'enable_time_boxing': config.status_mapping.enable_time_boxing,
                'enable_hackathon_features': config.status_mapping.enable_hackathon_features,
                'default_priority': config.status_mapping.default_priority,
                'escalation_threshold_hours': config.status_mapping.escalation_threshold_hours,
                'escalate_overdue': config.status_mapping.escalate_overdue,
                'escalate_critical_bugs': config.status_mapping.escalate_critical_bugs,
                'escalate_breaking_changes': config.status_mapping.escalate_breaking_changes,
                'max_dashboard_items': config.status_mapping.max_dashboard_items,
                'cache_dashboard_seconds': config.status_mapping.cache_dashboard_seconds,
            },
            'branch_naming': {
                'enforce_naming_convention': config.branch_naming.enforce_naming_convention,
                'allow_custom_patterns': config.branch_naming.allow_custom_patterns,
                'max_description_length': config.branch_naming.max_description_length,
                'min_description_length': config.branch_naming.min_description_length,
                'allowed_prefixes': config.branch_naming.allowed_prefixes,
                'require_issue_number': config.branch_naming.require_issue_number,
                'allow_special_chars': config.branch_naming.allow_special_chars,
                'case_sensitive': config.branch_naming.case_sensitive,
            },
            'testing': {
                'enable_performance_tests': config.testing.enable_performance_tests,
                'enable_security_tests': config.testing.enable_security_tests,
                'enable_integration_tests': config.testing.enable_integration_tests,
                'max_parse_time_ms': config.testing.max_parse_time_ms,
                'max_mapping_time_ms': config.testing.max_mapping_time_ms,
                'max_validation_time_ms': config.testing.max_validation_time_ms,
                'generate_large_datasets': config.testing.generate_large_datasets,
                'max_test_iterations': config.testing.max_test_iterations,
                'mock_api_delay_ms': config.testing.mock_api_delay_ms,
                'mock_failure_rate': config.testing.mock_failure_rate,
            },
            'debug_mode': config.debug_mode,
            'log_level': config.log_level,
            'environment': config.environment,
        }
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)
        
        # Save to file
        with open(file_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
        
        logger.info(f"Configuration saved to {file_path}")
    
    def get_config(self) -> SystemConfig:
        """Get current configuration (loads if not already loaded)"""
        return self.load_config()
    
    def reload_config(self) -> SystemConfig:
        """Reload configuration from file and environment"""
        self._config = None
        return self.load_config()

# Global configuration manager
config_manager = ConfigManager()

def get_config() -> SystemConfig:
    """Get the global configuration"""
    return config_manager.get_config()

def reload_config() -> SystemConfig:
    """Reload the global configuration"""
    return config_manager.reload_config()

# Convenience functions for accessing specific configurations
def get_parsing_config() -> ParsingConfig:
    """Get parsing configuration"""
    return get_config().parsing

def get_status_mapping_config() -> StatusMappingConfig:
    """Get status mapping configuration"""
    return get_config().status_mapping

def get_branch_naming_config() -> BranchNamingConfig:
    """Get branch naming configuration"""
    return get_config().branch_naming

def get_testing_config() -> TestingConfig:
    """Get testing configuration"""
    return get_config().testing