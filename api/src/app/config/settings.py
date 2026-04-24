from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    database_host: str
    database_name: str
    database_user: str
    database_password: str
    pool_size:int=10
    max_overflow:int=30
    pool_timeout:int=30
    pool_recycle:int=1800
    db_port: int = 5432

    def db_url(self) -> str:
        """
        Returns the url/connection string for the datbase
        """
        return  (
            f"postgresql+asyncpg://{self.database_user}:{self.database_password}"
            f"@{self.database_host}:{self.db_port}/{self.database_name}")


settings = Settings() # type: ignore