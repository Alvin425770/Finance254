from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "254 Finance"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    #Using SQLite for local development. we will swap to Postgres for production
    DATABASE_URL: str = "sqlite:///./P2P_Lending.db"
    
    #safaricom daraja sandbox settings
    MPESA_ENVIRONMENT: str = "sandbox" #sandbox or production
    MPESA_CONSUMER_KEY: str = "YOUR_DARAJA_CONSUMER_KEY"
    MPESA_CONSUMER_SECRET: str = "YOUR_DARAJA_CONSUMER_SECRET"
    
    # safaricom sandbox shortcode (default paybill for testing is 174379)
    MPESA_BUSINESS_SHORTCODE: str = "174379"
    # Default Daraja sandbox Passkey
    MPESA_PASSKEY: str = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
    
    #Callback URL (where safaricom sends payment results)
    MPESA_CALLBACK_URL: str = "https://your-domain.com/api/v1/payments/mpesa/callbac"
    class Config:
        case_sensitive = True
        env_file = ".env"
        
settings = Settings()