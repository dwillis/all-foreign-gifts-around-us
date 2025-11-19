"""
Configuration loader utility for Foreign Gifts Tracker.
Supports loading from YAML files and environment variables.
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the application."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to YAML config file. If None, uses default locations.
        """
        self._config: Dict[str, Any] = {}
        self._load_env_variables()
        self._load_config_file(config_path)

    def _load_env_variables(self):
        """Load environment variables from .env file if it exists."""
        load_dotenv()

    def _load_config_file(self, config_path: Optional[str] = None):
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to config file. Tries multiple locations if None.
        """
        if config_path is None:
            # Try multiple locations
            possible_paths = [
                Path("config/config.yaml"),
                Path("config.yaml"),
                Path("../config/config.yaml"),
            ]
            for path in possible_paths:
                if path.exists():
                    config_path = str(path)
                    break

        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key path.

        Args:
            key: Dot-separated key path (e.g., "api.anthropic_key")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        # First try environment variable
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        if env_value is not None:
            return env_value

        # Then try config file
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    @property
    def anthropic_api_key(self) -> str:
        """Get Anthropic API key."""
        return self.get('api.anthropic_key', os.getenv('ANTHROPIC_API_KEY', ''))

    @property
    def groq_api_key(self) -> str:
        """Get Groq API key."""
        return self.get('api.groq_key', os.getenv('GROQ_API_KEY', ''))

    @property
    def database_path(self) -> Path:
        """Get full database path."""
        db_dir = Path(self.get('database.path', 'data/output'))
        db_name = self.get('database.name', 'gifts.db')
        return db_dir / db_name

    @property
    def paths(self) -> Dict[str, str]:
        """Get all configured paths."""
        return self.get('paths', {})


# Global config instance
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get or create global configuration instance.

    Args:
        config_path: Path to config file

    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
