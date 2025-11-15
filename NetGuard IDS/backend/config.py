from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://netguard_user:changeme123@localhost:5432/netguard"
    NETWORK_INTERFACE: str = "eth0"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        # Load environment variables from a .env file
        env_file = ".env"

# Create a single settings instance to be imported by other modules
settings = Settings()