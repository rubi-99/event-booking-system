from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_JWT_SECRET: str
    SUPABASE_SERVICE_ROLE_KEY: str
    DATABASE_URL: str
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    SUPABASE_STORAGE_BUCKET: str = "event-posters"
    EMAIL_PROVIDER: str = "dev"
    EMAIL_PROVIDER_KEY: str = ""
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 300

    # This configuration tells Pydantic to read from a local .env file
    # and ignore any extra variables it doesn't need.
    # Note: since the config file is now in app/config/config.py,
    # env_file should point to "../../.env" or Pydantic will search from the current working directory (which is the project root).
    # Pydantic Settings defaults to searching from the CWD, which is the project root.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
