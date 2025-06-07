"""Configuration management for Flight Delay Explorer."""
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = ConfigDict(
        env_prefix="FLIGHT_",
        case_sensitive=False
    )
    
    access_key: str = Field(..., description="AviationStack API access key")
    base_url: str = Field(
        default="https://api.aviationstack.com/v1",
        description="API base URL"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts"
    )
    timeout_seconds: int = Field(
        default=30,
        description="Request timeout in seconds"
    )