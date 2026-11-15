from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "254 Finance"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    #Using SQLite for local development. we will swap to Postgres for production
    DATABASE_URL: str = "sqlite:///./P2P_Lending.db"
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        
settings = Settings()