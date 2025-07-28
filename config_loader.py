#!/usr/bin/env python3
"""
Secure Configuration Loader for ApplyX
======================================
This module provides secure configuration loading that uses environment variables
as fallbacks for sensitive data, preventing secrets from being committed to git.
"""

import os
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def load_secure_config(config_path='config.yaml'):
    """
    Load configuration from YAML file with environment variable fallbacks.
    
    This function:
    1. Loads config from YAML file if it exists
    2. Falls back to environment variables for sensitive data
    3. Provides secure defaults if neither are available
    
    Args:
        config_path (str): Path to the YAML configuration file
        
    Returns:
        dict: Complete configuration dictionary
    """
    config = {}
    
    # Try to load from YAML file first
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as stream:
                config = yaml.safe_load(stream) or {}
                logger.info(f"✅ Configuration loaded from {config_path}")
        except yaml.YAMLError as e:
            logger.error(f"❌ Error parsing {config_path}: {e}")
            config = {}
        except Exception as e:
            logger.error(f"❌ Error loading {config_path}: {e}")
            config = {}
    else:
        logger.warning(f"⚠️ Configuration file {config_path} not found, using environment variables and defaults")
    
    # Apply environment variable overrides for sensitive data
    config = apply_env_overrides(config)
    
    # Apply secure defaults
    config = apply_secure_defaults(config)
    
    return config

def apply_env_overrides(config):
    """
    Apply environment variable overrides for sensitive configuration.
    
    Args:
        config (dict): Base configuration dictionary
        
    Returns:
        dict: Configuration with environment overrides applied
    """
    # Email credentials
    if os.getenv('LINKEDIN_EMAIL'):
        config['email'] = os.getenv('LINKEDIN_EMAIL')
    if os.getenv('LINKEDIN_PASSWORD'):
        config['password'] = os.getenv('LINKEDIN_PASSWORD')
    
    # LinkedIn credentials (alternative names)
    if os.getenv('LINKEDIN_EMAIL'):
        config['linkedinEmail'] = os.getenv('LINKEDIN_EMAIL')
    if os.getenv('LINKEDIN_PASSWORD'):
        config['linkedinPassword'] = os.getenv('LINKEDIN_PASSWORD')
    
    # OpenAI API Key
    if os.getenv('OPENAI_API_KEY'):
        config['openaiApiKey'] = os.getenv('OPENAI_API_KEY')
    
    # Application settings
    if os.getenv('MAX_APPLICATIONS_PER_DAY'):
        try:
            config['maxApplicationsPerDay'] = int(os.getenv('MAX_APPLICATIONS_PER_DAY'))
        except ValueError:
            logger.warning("⚠️ Invalid MAX_APPLICATIONS_PER_DAY value, using default")
    
    if os.getenv('AGENT_DELAY_MINUTES'):
        try:
            config['agentDelayMinutes'] = int(os.getenv('AGENT_DELAY_MINUTES'))
        except ValueError:
            logger.warning("⚠️ Invalid AGENT_DELAY_MINUTES value, using default")
    
    # File paths
    if os.getenv('UPLOAD_PATH'):
        config['outputFileDirectory'] = os.getenv('UPLOAD_PATH')
    
    return config

def apply_secure_defaults(config):
    """
    Apply secure default values for required configuration keys.
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        dict: Configuration with secure defaults applied
    """
    defaults = {
        # Credentials (empty by default - must be set by user)
        'email': '',
        'password': '',
        'linkedinEmail': '',
        'linkedinPassword': '',
        'openaiApiKey': '',
        
        # Bot behavior
        'disableAntiLock': False,
        'remote': True,
        'lessthanTenApplicants': False,
        'newestPostingsFirst': False,
        
        # Experience levels
        'experienceLevel': {
            'internship': False,
            'entry': True,
            'associate': False,
            'mid-senior level': False,
            'director': False,
            'executive': False
        },
        
        # Job types
        'jobTypes': {
            'full-time': True,
            'contract': True,
            'part-time': False,
            'temporary': False,
            'internship': False,
            'other': False,
            'volunteer': False
        },
        
        # Date filters
        'date': {
            'all time': True,
            'month': False,
            'week': False,
            '24 hours': False
        },
        
        # Default positions and locations
        'positions': ['Software Engineer', 'Developer'],
        'locations': ['Remote'],
        
        # Other settings
        'residentStatus': False,
        'distance': 100,
        'outputFileDirectory': './output',
        'companyBlacklist': None,
        'titleBlacklist': None,
        'posterBlacklist': None,
        
        # File uploads
        'uploads': {
            'resume': ''
        },
        
        # Checkbox preferences
        'checkboxes': {
            'driversLicence': True,
            'requireVisa': False,
            'legallyAuthorized': True,
            'certifiedProfessional': True,
            'urgentFill': True,
            'commute': True,
            'remote': True,
            'drugTest': True,
            'assessment': True,
            'securityClearance': False,
            'degreeCompleted': ['Bachelor\'s Degree'],
            'backgroundCheck': True
        },
        
        # Personal information
        'universityGpa': 3.5,
        'salaryMinimum': 50000,
        'languages': {
            'english': 'Native or bilingual'
        },
        'noticePeriod': 2,
        
        # Personal info structure
        'personalInfo': {
            'First Name': '',
            'Last Name': '',
            'Phone': '',
            'Website': ''
        },
        
        # EEO information
        'eeo': {
            'race': '',
            'gender': '',
            'veteran': '',
            'disability': ''
        },
        
        # Experience
        'experience': {
            'default': ''
        }
    }
    
    # Merge defaults with existing config (existing values take precedence)
    for key, default_value in defaults.items():
        if key not in config:
            config[key] = default_value
        elif isinstance(default_value, dict) and isinstance(config[key], dict):
            # For dictionaries, merge recursively
            for sub_key, sub_default in default_value.items():
                if sub_key not in config[key]:
                    config[key][sub_key] = sub_default
    
    return config

def validate_config(config):
    """
    Validate that the configuration has all required fields.
    
    Args:
        config (dict): Configuration dictionary to validate
        
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    
    # Check for required fields
    required_fields = [
        'email', 'password', 'positions', 'locations',
        'experienceLevel', 'jobTypes', 'date', 'checkboxes'
    ]
    
    for field in required_fields:
        if field not in config:
            errors.append(f"Missing required field: {field}")
    
    # Validate email format if present
    if config.get('email'):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, config['email']):
            errors.append("Invalid email format")
    
    # Check that at least one position is specified
    if not config.get('positions') or len(config['positions']) == 0:
        errors.append("At least one job position must be specified")
    
    # Check that at least one location is specified
    if not config.get('locations') or len(config['locations']) == 0:
        errors.append("At least one location must be specified")
    
    # Check OpenAI API key format if present
    openai_key = config.get('openaiApiKey', '')
    if openai_key and not openai_key.startswith('sk-'):
        errors.append("OpenAI API key should start with 'sk-'")
    
    return len(errors) == 0, errors

def get_masked_config(config):
    """
    Get a version of the config with sensitive data masked for logging.
    
    Args:
        config (dict): Configuration dictionary
        
    Returns:
        dict: Configuration with sensitive data masked
    """
    sensitive_fields = ['password', 'linkedinPassword', 'openaiApiKey']
    masked_config = config.copy()
    
    for field in sensitive_fields:
        if field in masked_config and masked_config[field]:
            value = masked_config[field]
            if len(value) > 8:
                masked_config[field] = value[:4] + '*' * (len(value) - 8) + value[-4:]
            else:
                masked_config[field] = '*' * len(value)
    
    return masked_config

# Convenience function for backward compatibility
def load_config(config_path='config.yaml'):
    """
    Load configuration (backward compatibility function).
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        dict: Configuration dictionary
    """
    return load_secure_config(config_path) 