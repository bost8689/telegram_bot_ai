import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
load_dotenv()

class Settings(BaseSettings):   

    APP_ENV: str  
    DEBUG: str
    DATABASE_URL_ASYNC: str  
    TG_BOT_TOKEN:str
    TG_BOT_ID:int
    TG_CHAT_ID:int
    AI_TOKEN:str
    AI_API_URL:str
    
    @property
    def DATABASE_URL_SYNC(self) -> str:
        if self.DATABASE_URL_ASYNC.startswith("postgresql+asyncpg://"):
            return self.DATABASE_URL_ASYNC.replace("postgresql+asyncpg://", "postgresql://", 1)
        elif self.DATABASE_URL_ASYNC.startswith("postgresql://"):
            # Уже синхронный — ок
            return self.DATABASE_URL_ASYNC
        else:
            raise ValueError("Unsupported database URL scheme")
        
    class Config:
        env_file = ".env" # игнорируется т.к переопределяю ниже
        env_file_encoding = "utf-8"
        extra = "ignore"

# Фабрика настроек с выбором .env-файла
def get_settings() -> Settings:
    import os
    app_env = os.getenv("APP_ENV", "development")    
    env_file = {
        "development": ".env.development",
        "production": ".env.production",
    }.get(app_env, ".env.production")
    
    return Settings(_env_file=env_file)

settings = get_settings()