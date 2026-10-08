from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Production Incident Investigator"
    environment: str = "development"
    log_level: str = "INFO"

    llm_provider: str = ""
    llm_model: str = ""
    llm_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
