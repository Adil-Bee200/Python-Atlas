import os
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    database_url: str | None = None

    database_hostname : str = "localhost"
    database_port : str = "5432"
    database_password : str = "pass"
    database_name : str = "db"
    database_username : str = "user"
    secret_key : str 
    algorithm : str 
    access_token_expire_minutes : str

    @property
    def sqlalchemy_database_url(self):
        if self.database_url:
            return self.database_url
        return (
            f'postgresql://{self.database_username}:{self.database_password}@{self.database_hostname}:{self.database_port}/{self.database_name}'
        )
    
    model_config = SettingsConfigDict(
        env_file=".env" if os.getenv("RAILWAY_ENVIRONMENT") is None else None
    )

    ##class Config:              <UNCOMMENT THIS FOR LOCAL RUNNING>
        ##env_file = ".env"

settings = Settings()