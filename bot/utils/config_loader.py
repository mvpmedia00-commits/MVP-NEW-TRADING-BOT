"""
Configuration loader utility
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from .logger import get_logger

logger = get_logger(__name__)


class ConfigLoader:
    """Load and manage configuration files"""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the config loader
        
        Args:
            config_dir: Path to configuration directory
        """
        # Load environment variables
        load_dotenv()
        
        # Set config directory
        if config_dir is None:
            base_dir = Path(__file__).parent.parent.parent
            self.config_dir = base_dir / "config"
        else:
            self.config_dir = Path(config_dir)
        
        logger.info(f"Config directory: {self.config_dir}")
        
        # Cache for loaded configs
        self._cache: Dict[str, Any] = {}
    
    def load_global_config(self) -> Dict[str, Any]:
        """Load global configuration"""
        return self._load_json("global.json")
    
    def load_broker_config(self, broker_name: str) -> Dict[str, Any]:
        """
        Load broker-specific configuration
        
        Args:
            broker_name: Name of the broker (e.g., 'binance', 'coinbase')
            
        Returns:
            Broker configuration dictionary
        """
        config_file = f"brokers/{broker_name}.json"
        config = self._load_json(config_file, required=False)
        
        if config is None:
            logger.warning(f"Broker config not found: {broker_name}")
            return {}
        
        # Override with environment variables if available
        config = self._apply_env_overrides(config, broker_name.upper())
        
        return config
    
    def load_strategy_config(self) -> Dict[str, Any]:
        """Load strategy configuration"""
        return self._load_json("strategies/strategy_config.json")
    
    def get_enabled_brokers(self) -> list:
        """Get list of enabled brokers"""
        brokers_dir = self.config_dir / "brokers"
        enabled_brokers = []
        
        if not brokers_dir.exists():
            logger.warning("Brokers directory not found")
            return enabled_brokers
        
        for config_file in brokers_dir.glob("*.json"):
            if config_file.name.startswith("_"):
                continue
            
            broker_name = config_file.stem
            config = self.load_broker_config(broker_name)
            
            if config.get("enabled", False):
                enabled_brokers.append(broker_name)
        
        logger.info(f"Enabled brokers: {enabled_brokers}")
        return enabled_brokers
    
    def _load_json(self, relative_path: str, required: bool = True) -> Optional[Dict[str, Any]]:
        """
        Load JSON configuration file
        
        Args:
            relative_path: Path relative to config directory
            required: Whether the file is required
            
        Returns:
            Configuration dictionary or None
        """
        cache_key = relative_path
        
        # Return from cache if available
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        config_path = self.config_dir / relative_path
        
        if not config_path.exists():
            if required:
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            return None
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            self._cache[cache_key] = config
            logger.debug(f"Loaded config: {relative_path}")
            return config
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {config_path}: {e}")
            if required:
                raise
            return None
    
    def _apply_env_overrides(self, config: Dict[str, Any], prefix: str) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration
        
        Args:
            config: Configuration dictionary
            prefix: Environment variable prefix
            
        Returns:
            Updated configuration
        """
        # Override API credentials from environment
        if "api_credentials" in config:
            api_key_var = f"{prefix}_API_KEY"
            api_secret_var = f"{prefix}_API_SECRET"
            passphrase_var = f"{prefix}_PASSPHRASE"
            
            if os.getenv(api_key_var):
                config["api_credentials"]["api_key"] = os.getenv(api_key_var)
            if os.getenv(api_secret_var):
                config["api_credentials"]["api_secret"] = os.getenv(api_secret_var)
            if os.getenv(passphrase_var):
                config["api_credentials"]["passphrase"] = os.getenv(passphrase_var)
        
        # Override testnet setting
        testnet_var = f"{prefix}_TESTNET"
        if os.getenv(testnet_var) and "settings" in config:
            config["settings"]["testnet"] = os.getenv(testnet_var).lower() == 'true'
        
        return config
    
    def reload(self):
        """Clear cache and reload configurations"""
        self._cache.clear()
        logger.info("Configuration cache cleared")
