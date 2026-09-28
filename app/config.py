from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """Application configuration loaded from environment or .env file."""
    
    # API Credentials
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
    hf_api_key: str = Field(default="", validation_alias="HF_API_KEY")
    
    # AI Models
    gemini_flash_model: str = Field(default="gemini-1.5-flash", validation_alias="GEMINI_FLASH_MODEL")
    gemini_pro_model: str = Field(default="gemini-1.5-pro", validation_alias="GEMINI_PRO_MODEL")
    sd_model_id: str = Field(default="runwayml/stable-diffusion-v1-5", validation_alias="SD_MODEL_ID")
    
    # Server Settings
    host: str = Field(default="127.0.0.1", validation_alias="HOST")
    port: int = Field(default=8000, validation_alias="PORT")
    debug: bool = Field(default=True, validation_alias="DEBUG")
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    
    # Directory paths
    base_dir: Path = BASE_DIR
    static_dir: Path = BASE_DIR / "static"
    templates_dir: Path = BASE_DIR / "templates"
    panels_dir: Path = BASE_DIR / "static" / "panels"
    exports_dir: Path = BASE_DIR / "static" / "exports"
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist
settings.panels_dir.mkdir(parents=True, exist_ok=True)
settings.exports_dir.mkdir(parents=True, exist_ok=True)
