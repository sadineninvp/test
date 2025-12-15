"""
Configuration management for IQIDE client
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Manages client configuration"""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration
        
        Args:
            config_file: Path to config file (defaults to ~/.iqide/config.json)
        """
        if config_file:
            self.config_file = Path(config_file)
        else:
            # Default: ~/.iqide/config.json
            home = Path.home()
            self.config_dir = home / ".iqide"
            self.config_file = self.config_dir / "config.json"
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or create default config
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load config from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except Exception:
                # If file is corrupted, use defaults
                pass
        
        # Default configuration
        default_config = {
            "api_url": "http://localhost:8000",
            "default_use_llm": False,
            "timeout": 1800,  # 30 minutes (1800 seconds)
            "output_format": "pretty"  # "pretty" or "json"
        }
        
        # Save default config
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save config to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set config value and save"""
        self.config[key] = value
        self._save_config(self.config)
    
    def get_api_url(self) -> str:
        """Get API URL"""
        return self.config.get("api_url", "http://localhost:8000")
    
    def get_default_use_llm(self) -> bool:
        """Get default use_llm setting"""
        return self.config.get("default_use_llm", False)
    
    def get_timeout(self) -> int:
        """Get request timeout"""
        return self.config.get("timeout", 1800)  # Default: 30 minutes
    
    def get_output_format(self) -> str:
        """Get output format"""
        return self.config.get("output_format", "pretty")

