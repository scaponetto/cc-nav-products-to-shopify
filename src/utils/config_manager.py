"""
Configuration manager for handling configuration files and environment variables.
"""

import os
import yaml
from typing import Any, Dict
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    host: str
    port: int
    user: str
    password: str
    name: str

@dataclass
class ShopifyConfig:
    shop_domain: str
    access_token: str
    api_version: str
    timeout: int

@dataclass
class ProcessingConfig:
    max_retries: int
    retry_delay: float
    batch_size: int
    rate_limit_per_second: int

@dataclass
class LoggingConfig:
    level: str
    file: str
    max_size: str
    backup_count: int

class ConfigManager:
    """Manages configuration from files and environment variables"""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file and environment variables"""
        with open(self.config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Process environment variable substitution
        config_data = self._substitute_env_vars(config_data)
        
        # Create configuration objects
        self.database = DatabaseConfig(**config_data['database'])
        self.shopify = ShopifyConfig(**config_data['shopify'])
        self.processing = ProcessingConfig(**config_data['processing'])
        self.logging = LoggingConfig(**config_data['logging'])
    
    def _substitute_env_vars(self, data: Any) -> Any:
        """Recursively substitute environment variables in configuration"""
        if isinstance(data, dict):
            return {key: self._substitute_env_vars(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(item) for item in data]
        elif isinstance(data, str):
            return self._expand_env_vars(data)
        else:
            return data
    
    def _expand_env_vars(self, text: str) -> str:
        """Expand environment variables in text"""
        import re
        
        def replace_env_var(match):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) else ''
            return os.getenv(var_name, default_value)
        
        # Pattern: ${VAR_NAME:default_value}
        pattern = r'\$\{([^:]+):?([^}]*)\}'
        return re.sub(pattern, replace_env_var, text)
