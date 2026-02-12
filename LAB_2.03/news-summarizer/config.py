"""Configuration management for news summarizer."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration loaded from environment variables."""
    
    # API Keys (loaded from .env)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    
    # Environment (development, staging, or production)
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # API Configuration
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    
    # Which AI models to use
    OPENAI_MODEL = "gpt-4o-mini"
    ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"
    
    # Cost Control
    DAILY_BUDGET = float(os.getenv("DAILY_BUDGET", "5.00"))
    
    # Rate Limits (how many requests per minute we're allowed)
    OPENAI_RPM = 500
    ANTHROPIC_RPM = 50
    NEWS_API_RPM = 100
    
    @classmethod
    def validate(cls):
        """Check that all required API keys are set."""
        required = [
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
            ("ANTHROPIC_API_KEY", cls.ANTHROPIC_API_KEY),
            ("NEWS_API_KEY", cls.NEWS_API_KEY)
        ]
        
        # Find which keys are missing
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        print(f"Configuration validated for {cls.ENVIRONMENT} environment")

# Validate on import
Config.validate()