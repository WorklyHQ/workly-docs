"""
Configuration manager for Desktop-Mate.
Handles loading and saving user preferences.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class Config:
    """Application configuration manager."""
    
    DEFAULT_CONFIG_FILE = "config.json"
    
    def __init__(self, config_path: str = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Optional path to config file
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Store config in user's app data directory
            app_dir = Path.home() / ".desktop-mate"
            app_dir.mkdir(exist_ok=True)
            self.config_path = app_dir / self.DEFAULT_CONFIG_FILE
            
        self.config: Dict[str, Any] = {}
        self.load()
        
    def load(self):
        """Load configuration from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to load configuration: {e}")
                self.config = self._get_default_config()
        else:
            logger.info("No configuration file found, using defaults")
            self.config = self._get_default_config()
            
    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Saved configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'unity.port')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any):
        """Set a configuration value.
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        config[keys[-1]] = value
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration.
        
        Returns:
            Default configuration dictionary
        """
        return {
            "unity": {
                "host": "127.0.0.1",
                "port": 5555
            },
            "audio": {
                "sample_rate": 44100,
                "buffer_size": 1024,
                "device": None
            },
            "avatar": {
                "last_model": None,
                "default_model": None
            },
            "window": {
                "width": 800,
                "height": 600,
                "x": 100,
                "y": 100
            }
        }
