import os
import yaml
import logging
import secrets
import re
from typing import Dict, Any, Optional

class ConfigLoader:
    """
    Configuration loader for Caldera that supports environment variables and secure defaults.
    
    This class loads configuration from YAML files and allows overriding values
    with environment variables using the CALDERA_ prefix.
    """
    
    def __init__(self, config_path: str, env_prefix: str = 'CALDERA_'):
        """
        Initialize the configuration loader.
        
        Args:
            config_path: Path to the YAML configuration file
            env_prefix: Prefix for environment variables to override configuration
        """
        self.config_path = config_path
        self.env_prefix = env_prefix
        self.logger = logging.getLogger('config_loader')
        
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file and override with environment variables.
        
        Returns:
            Dict containing the merged configuration
        """
        # Load base configuration from YAML
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
        else:
            self.logger.warning(f"Configuration file {self.config_path} not found, using empty configuration")
            config = {}
            
        # Override with environment variables
        config = self._override_from_env(config)
        
        # Apply secure defaults for sensitive values
        config = self._apply_secure_defaults(config)
        
        return config
    
    def _override_from_env(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override configuration values with environment variables.
        
        Environment variables should be prefixed with CALDERA_ and use underscores
        to represent nested keys. For example, CALDERA_APP_HOST would override app.host.
        
        Args:
            config: Base configuration dictionary
            
        Returns:
            Updated configuration dictionary
        """
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # Remove prefix and convert to lowercase
                config_key = key[len(self.env_prefix):].lower()
                
                # Handle nested keys (convert underscores to dots)
                if '_' in config_key:
                    # Convert to nested dictionary keys
                    parts = config_key.split('_')
                    current = config
                    for part in parts[:-1]:
                        if part not in current:
                            current[part] = {}
                        elif not isinstance(current[part], dict):
                            # If the current value is not a dict, convert it to a dict
                            current[part] = {}
                        current = current[part]
                    current[parts[-1]] = self._convert_value(value)
                else:
                    # Direct key
                    config[config_key] = self._convert_value(value)
                    
        return config
    
    def _convert_value(self, value: str) -> Any:
        """
        Convert string values to appropriate types.
        
        Args:
            value: String value from environment variable
            
        Returns:
            Converted value (bool, int, float, or string)
        """
        # Convert boolean values
        if value.lower() in ('true', 'yes', '1'):
            return True
        if value.lower() in ('false', 'no', '0'):
            return False
            
        # Convert numeric values
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
            
        # Handle lists (comma-separated values)
        if ',' in value:
            return [self._convert_value(v.strip()) for v in value.split(',')]
            
        # Return as string
        return value
    
    def _apply_secure_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply secure defaults for sensitive configuration values.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Updated configuration dictionary with secure defaults
        """
        # Generate secure encryption key if not set
        if not config.get('encryption_key'):
            config['encryption_key'] = secrets.token_hex(16)
            self.logger.warning("Generated random encryption_key")
            
        # Generate secure crypt_salt if not set
        if not config.get('crypt_salt'):
            config['crypt_salt'] = secrets.token_hex(8)
            self.logger.warning("Generated random crypt_salt")
            
        # Handle users configuration
        if 'users' in config:
            # Check if admin user exists with default password
            for username, password in config['users'].items():
                if username in ('admin', 'red') and password == 'admin':
                    self.logger.warning(f"User '{username}' has default password. Consider changing it.")
                    
        # Handle API keys
        if config.get('api_key_red') == 'ADMIN123':
            self.logger.warning("Using default Red API key. Consider changing it.")
            
        if config.get('api_key_blue') == 'BLUEADMIN123':
            self.logger.warning("Using default Blue API key. Consider changing it.")
            
        return config
    
    def save(self, config: Dict[str, Any], output_path: Optional[str] = None) -> None:
        """
        Save configuration to a YAML file.
        
        Args:
            config: Configuration dictionary to save
            output_path: Path to save the configuration (defaults to self.config_path)
        """
        output_path = output_path or self.config_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
            
        self.logger.info(f"Configuration saved to {output_path}")


def load_config(config_name: str = 'main', env_file: str = None) -> Dict[str, Any]:
    """
    Helper function to load configuration.
    
    Args:
        config_name: Name of the configuration (main, agents, payloads)
        env_file: Path to .env file to load (optional)
        
    Returns:
        Configuration dictionary
    """
    # Load .env file if provided
    if env_file and os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    # Determine configuration file path
    env = os.environ.get('CALDERA_ENVIRONMENT', 'local')
    if config_name == 'main':
        config_path = f"conf/{env}.yml"
    else:
        config_path = f"conf/{config_name}.yml"
        
    # Load configuration
    loader = ConfigLoader(config_path)
    return loader.load()
