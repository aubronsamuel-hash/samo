from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./planninghub.db"
    redis_url: str = "redis://localhost:6379/0"
    auth0_domain: str = ""
    auth0_api_audience: str = ""
    auth0_algorithms: str = "RS256"
    secret_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
