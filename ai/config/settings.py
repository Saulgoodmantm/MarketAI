"""
Settings Module - Manages AI configuration
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Settings:
    """
    Manages MarketAI settings and configuration.
    Supports local storage and modification.
    """
    
    DEFAULT_CONFIG_PATH = Path("shared_data/config.json")
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize settings manager.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path) if config_path else self.DEFAULT_CONFIG_PATH
        self._settings = self._load_defaults()
        self._load_config()
        
    def _load_defaults(self) -> Dict[str, Any]:
        """Load default settings."""
        return {
            # Model settings
            'model_path': 'shared_data/models/market_ai.model',
            'model_version': '1.0.0',
            
            # Training settings
            'training': {
                'enabled': True,
                'auto_train': True,
                'epochs': 10,
                'batch_size': 32,
                'learning_rate': 0.001,
                'min_samples': 100
            },
            
            # Detection settings
            'detection': {
                'screen': {
                    'enabled': True,
                    'interval': 1.0,
                    'ocr_enabled': True,
                    'object_detection_enabled': True
                },
                'web': {
                    'enabled': True,
                    'headless': True,
                    'timeout': 30000,
                    'extract_text': True,
                    'extract_links': True,
                    'extract_images': True
                }
            },
            
            # Data sharing settings
            'shared_data': {
                'path': 'shared_data',
                'sync_interval': 60,
                'max_history': 1000
            },
            
            # UI settings
            'ui': {
                'theme': 'dark',
                'accent_color': '#00D4FF',
                'font_family': 'Segoe UI',
                'animations': True
            },
            
            # System settings
            'system': {
                'log_level': 'INFO',
                'max_memory_mb': 4096,
                'thread_pool_size': 4
            }
        }
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    self._merge_settings(loaded)
        except Exception as e:
            print(f"[WARNING] Failed to load config: {e}")
    
    def _merge_settings(self, loaded: Dict[str, Any]):
        """Merge loaded settings with defaults."""
        def merge(base, update):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge(base[key], value)
                else:
                    base[key] = value
        
        merge(self._settings, loaded)
    
    def save(self):
        """Save current settings to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key (supports dot notation: 'training.epochs')
            default: Default value if key not found
            
        Returns:
            Setting value
        """
        keys = key.split('.')
        value = self._settings
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any, auto_save: bool = True) -> bool:
        """
        Set a setting value.
        
        Args:
            key: Setting key (supports dot notation)
            value: Value to set
            auto_save: Whether to save after setting
            
        Returns:
            True if successful
        """
        keys = key.split('.')
        target = self._settings
        
        try:
            for k in keys[:-1]:
                if k not in target:
                    target[k] = {}
                target = target[k]
            
            target[keys[-1]] = value
            
            if auto_save:
                return self.save()
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to set config: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings."""
        return self._settings.copy()
    
    def reset_to_defaults(self, auto_save: bool = True) -> bool:
        """Reset all settings to defaults."""
        self._settings = self._load_defaults()
        if auto_save:
            return self.save()
        return True
    
    def update(self, settings: Dict[str, Any], auto_save: bool = True) -> bool:
        """
        Update multiple settings at once.
        
        Args:
            settings: Dictionary of settings to update
            auto_save: Whether to save after updating
            
        Returns:
            True if successful
        """
        self._merge_settings(settings)
        if auto_save:
            return self.save()
        return True
