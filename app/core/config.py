from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )
    app_name: str = 'searching-service'
    debug: bool = False
    database_url: str = 'postgresql+asyncpg://postgres:postgres@localhost:5432/searching_service'
    elasticsearch_url: str = 'http://localhost:9200'


settings = Settings()
