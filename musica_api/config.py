"""
Configuración de la aplicación.
Maneja diferentes entornos: desarrollo, pruebas y producción.
"""

from typing import Literal
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuración de la aplicación usando Pydantic Settings.
    Lee las variables de entorno desde el archivo .env
    """
    
    # Configuración básica de la aplicación
    app_name: str = "API de Música"
    app_version: str = "1.0.0"
    
    # Configuración del entorno
    environment: Literal["development", "testing", "production"] = "development"
    
    # Configuración de la base de datos
    database_url: str = "sqlite:///./musica.db"
    
    # Configuración del servidor
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Configuración de CORS
    cors_origins: list[str] = ["*"]
    
    # Configuración de seguridad
    secret_key: str = "super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Configuración de logging
    log_level: str = "INFO"
    
    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validación personalizada para la URL de la base de datos."""
        if not v or not v.strip():
            raise ValueError("DATABASE_URL no puede estar vacío")
        return v

    class Config:
        """Configuración de Pydantic Settings."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instancia global base
settings = Settings()


class DevelopmentSettings(Settings):
    """Configuración para el entorno de desarrollo."""
    debug: bool = True
    log_level: str = "DEBUG"


class TestingSettings(Settings):
    """Configuración para el entorno de pruebas."""
    environment: Literal["development", "testing", "production"] = "testing"
    database_url: str = "sqlite:///./test_musica.db"
    debug: bool = True
    log_level: str = "WARNING"


class ProductionSettings(Settings):
    """Configuración para el entorno de producción."""
    environment: Literal["development", "testing", "production"] = "production"
    debug: bool = False
    log_level: str = "ERROR"
    cors_origins: list[str] = ["https://midominio.com"]
    database_url: str = "postgresql://user:password@localhost/musica_prod"


def get_settings() -> Settings:
    """Retorna la configuración apropiada según el entorno."""
    env = settings.environment.lower()
    
    if env == "testing":
        return TestingSettings()
    elif env == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()


def validate_settings():
    """Valida que todas las configuraciones necesarias estén presentes al inicio."""
    required_settings = ["database_url", "app_name", "secret_key"]
    current_settings = get_settings()
    for setting in required_settings:
        if not getattr(current_settings, setting, None):
            raise ValueError(f"Configuración requerida no encontrada: {setting}")