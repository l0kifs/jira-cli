from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Main application settings"""

    model_config = SettingsConfigDict(
        env_prefix="JIRA_CLI__",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = Field(default="jira-cli", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")

    # Logging settings    
    log_level: str = Field(default="INFO", description="Logging level")
    log_file_dir: str = Field(
        default="logs", description="Directory for log files"
    )

    # Jira settings
    jira_domain: str = Field(
        default="", description="Jira instance domain (e.g., your-domain.atlassian.net)"
    )
    jira_email: str = Field(
        default="", description="Email associated with your Jira account"
    )
    jira_api_token: str = Field(
        default="", description="API token for authenticating with Jira"
    )


def get_settings() -> Settings:
    """Retrieve application settings"""
    return Settings()
