"""
Configuration management module for AI Pre-Call Briefing Assistant.

This module handles environment variable loading, validation, and provides
structured access to application configuration with proper error handling.
"""

import os
from typing import Optional
from dotenv import load_dotenv
import logging

# Configure logging for configuration issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass

class AppConfig:
    """
    Application configuration with validation and type safety.
    
    Provides centralized configuration management with proper validation,
    fallback values, and clear error reporting for missing critical settings.
    """
    
    def __init__(self):
        """Initialize configuration with validation."""
        self._validate_required_env_vars()
        
    @property
    def groq_api_key(self) -> Optional[str]:
        """Groq API key for AI briefing generation."""
        return os.getenv("GROQ_API_KEY")
    
    @property
    def news_api_key(self) -> Optional[str]:
        """News API key for fetching company news."""
        return os.getenv("NEWS_API_KEY")
    
    @property
    def salesforce_username(self) -> Optional[str]:
        """Salesforce username for CRM integration."""
        return os.getenv("SALESFORCE_USERNAME")
    
    @property
    def salesforce_password(self) -> Optional[str]:
        """Salesforce password for CRM integration."""
        return os.getenv("SALESFORCE_PASSWORD")
    
    @property
    def salesforce_security_token(self) -> Optional[str]:
        """Salesforce security token for CRM integration."""
        return os.getenv("SALESFORCE_SECURITY_TOKEN")
    
    @property
    def is_groq_configured(self) -> bool:
        """Check if Groq API is properly configured."""
        return (self.groq_api_key is not None and 
                self.groq_api_key != "gsk_YourGroqAPIKey" and 
                len(self.groq_api_key.strip()) > 0)
    
    @property
    def is_news_api_configured(self) -> bool:
        """Check if News API is properly configured."""
        return (self.news_api_key is not None and 
                self.news_api_key != "YourNewsAPIKey" and 
                len(self.news_api_key.strip()) > 0)
    
    @property
    def is_salesforce_configured(self) -> bool:
        """Check if Salesforce is properly configured for production use."""
        return (self.salesforce_username is not None and 
                self.salesforce_password is not None and 
                self.salesforce_security_token is not None and
                self.salesforce_username != "your.salesforce@email.com" and
                all(len(str(val).strip()) > 0 for val in [
                    self.salesforce_username, 
                    self.salesforce_password, 
                    self.salesforce_security_token
                ]))
    
    def _validate_required_env_vars(self) -> None:
        """Validate that .env file exists and warn about missing configurations."""
        env_file_path = os.path.join(os.getcwd(), '.env')
        
        if not os.path.exists(env_file_path):
            logger.warning(
                "No .env file found. Please create one using .env.example as template."
            )
        
        # Log configuration status for transparency
        config_status = {
            "Groq API": self.is_groq_configured,
            "News API": self.is_news_api_configured,
            "Salesforce": self.is_salesforce_configured
        }
        
        for service, configured in config_status.items():
            status = "✅ Configured" if configured else "⚠️  Not configured"
            logger.info(f"{service}: {status}")

# Create global configuration instance
config = AppConfig()

# Backward compatibility - maintain original interface
GROQ_API_KEY = config.groq_api_key
NEWS_API_KEY = config.news_api_key
SALESFORCE_USERNAME = config.salesforce_username
SALESFORCE_PASSWORD = config.salesforce_password
SALESFORCE_SECURITY_TOKEN = config.salesforce_security_token 