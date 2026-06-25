"""
Configuration settings using Pydantic
Loads environment variables and validates configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # WhatsApp Business API
    whatsapp_client_id: Optional[str] = None
    whatsapp_token: str
    whatsapp_verify_token: str = "my_verify_token_123"
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_api_url: str = "https://graph.facebook.com/v21.0"

    # PostgreSQL (Railway provee DATABASE_URL automáticamente)
    database_url: str

    # Supabase (deprecado — se migró a PostgreSQL en Railway)
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None

    # Google Gemini
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash-exp"

    # Google Calendar
    google_credentials: str  # Service Account credentials JSON
    google_calendar_id: str = "primary"

    # Legacy OAuth fields (deprecated, usar google_credentials)
    google_calendar_client_id: Optional[str] = None
    google_calendar_client_secret: Optional[str] = None
    google_calendar_redirect_uri: str = "http://localhost:8000/auth/callback"
    google_calendar_token_file: str = "token.json"

    # Application
    timezone: str = "America/Argentina/Buenos_Aires"
    debug: bool = True

    @property
    def tz(self):
        """Get timezone object"""
        import pytz
        return pytz.timezone(self.timezone)

    @property
    def TIMEZONE(self):
        return self.timezone

    @property
    def DEBUG(self):
        return self.debug

    @property
    def GEMINI_MODEL(self):
        return self.gemini_model

    @property
    def GOOGLE_CREDENTIALS(self):
        return self.google_credentials


# Global settings instance
settings = Settings()
