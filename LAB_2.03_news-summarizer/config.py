"""Configuration management for news summarizer."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

class Config:
    """Application configuration."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # API Configuration
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Models
    OPENAI_MODEL = "gpt-4o-mini"
    ANTHROPIC_MODEL = "claude-sonnet-4-5-20250929"
    
    # Cost Control
    DAILY_BUDGET = float(os.getenv("DAILY_BUDGET", "5.00"))
    
    # Rate Limits (requests per minute)
    OPENAI_RPM = 500
    ANTHROPIC_RPM = 50
    NEWS_API_RPM = 100
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        required = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
            ("ANTHROPIC_API_KEY", cls.ANTHROPIC_API_KEY),
            ("NEWS_API_KEY", cls.NEWS_API_KEY)
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        print(f"✓ Configuration validated for {cls.ENVIRONMENT} environment")

# Validate on import
Config.validate()
