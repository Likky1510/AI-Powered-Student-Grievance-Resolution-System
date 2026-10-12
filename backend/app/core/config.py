"""
Central configuration for the app.
Reads from a .env file (see .env.example). Any value left as "mock"
tells the relevant service module to skip the real API call and
return a simulated response instead, so the whole app runs end-to-end
even before you have real API keys.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./grievance.db"

    # Auth
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Claude
    anthropic_api_key: str = "mock"
    claude_model: str = "claude-sonnet-4-6"

    # SendGrid
    sendgrid_api_key: str = "mock"
    sendgrid_from_email: str = "noreply@yourcollege.edu"

    # Twilio
    twilio_account_sid: str = "mock"
    twilio_auth_token: str = "mock"
    twilio_whatsapp_from: str = "whatsapp:+14155238886"
    admin_whatsapp_to: str = "whatsapp:+91XXXXXXXXXX"

    environment: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def claude_is_mocked(self) -> bool:
        return self.anthropic_api_key.lower() == "mock"

    @property
    def sendgrid_is_mocked(self) -> bool:
        return self.sendgrid_api_key.lower() == "mock"

    @property
    def twilio_is_mocked(self) -> bool:
        return self.twilio_account_sid.lower() == "mock"


@lru_cache
def get_settings() -> Settings:
    return Settings()
