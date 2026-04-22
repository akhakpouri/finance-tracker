from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_host: str
    database_name: str
    database_user: str
    database_password: str
    db_port: int = 5432

    def db_url(self) -> str:
        """
        Returns the url/connection string for the datbase
        """
        return  f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.db_port}/{self.database_name}"


settings = Settings() # type: ignore