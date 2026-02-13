from pydantic_settings import BaseSettings
from typing import Optional, List


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando variables de entorno
    """
    # Configuración general
    PROJECT_NAME: str = "InfoRocha Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # Seguridad
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS - comma-separated origins or "*" for all
    CORS_ORIGINS: str = "*"
    
    # Base de datos - URL directa (preferida para deploy, ej: Render provee DATABASE_URL)
    DATABASE_URL_OVERRIDE: Optional[str] = None
    
    # Base de datos MySQL (fallback para desarrollo local)
    MYSQL_USER: str = ""
    MYSQL_PASSWORD: str = ""
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = ""
    
    @property
    def DATABASE_URL(self) -> str:
        """Construye la URL de conexión. Prioriza DATABASE_URL_OVERRIDE si existe."""
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parsea CORS_ORIGINS en una lista."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()
