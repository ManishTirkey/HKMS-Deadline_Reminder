import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Use modern Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="",  # No prefix for environment variables
        extra="ignore"  # Ignore extra environment variables
    )

    # Database Configuration (Updated to PostgreSQL)
    database_url: str = "sqlite:///./hkms.db"

    # Application Configuration
    app_name: str = "HKMS Reminder Processing"
    app_version: str = "1.0.0"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # Reminder stuffs
    Reminder_URL: str = "https://docs.google.com/spreadsheets/d/14UJhZglME_ECLCYvNYMBNHwKjM7MJR-y/edit?gid=2039290562#gid=2039290562"
    Reminder_input_dir: str = "Reminder_Input_Files"

    # Security Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]


# Create settings instance
settings = Settings()


# Ensure required directories exist
def ensure_directories():
    """Create required directories if they don't exist"""
    directories = [
        "templates", # Optional template folder to include welcome page
        "logs",
        settings.Reminder_input_dir  # Added for reminder files
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# Load settings and ensure directories
try:
    ensure_directories()
except Exception as e:
    print(f"Warning: Could not create directories: {e}")
