from functools import lru_cache
from typing import Literal, Union

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Entorno y Servidor ---
    # Literal restringe los valores a exactamente estos tres.
    # Si alguien escribe ENVIRONMENT=produccion en .env, la app no arranca.
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # --- Metadatos de la API ---
    PROJECT_NAME: str = "InnovaLab - Asistente de Accesibilidad"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "0.1.0"

    # DEBUG False por defecto es la postura más segura.
    # En development se puede activar desde .env (DEBUG=true).
    # Controla: visibilidad de Swagger/ReDoc, nivel de detalle en errores.
    DEBUG: bool = False

    # Puerto del servidor (ge=1, le=65535 valida rango TCP válido con Pydantic)
    PORT: int = Field(default=8000, ge=1, le=65535)

    # --- Credenciales y Secretos ---
    # Sin default: si falta en .env, la app NO arranca (Fail-Fast).
    # SecretStr: previene que la clave se exponga en logs, tracebacks o repr().
    GEMINI_API_KEY: SecretStr

    # Modelo de Gemini a utilizar (configurable sin redeployar)
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # --- Seguridad / CORS ---
    # Acepta tanto lista Python como string separado por comas desde el .env
    # Ej. en .env: BACKEND_CORS_ORIGINS=https://mi-app.vercel.app,http://localhost:3000
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> list[str]:
        """Parsea orígenes CORS desde string CSV o lista directa."""
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(f"Formato no válido para BACKEND_CORS_ORIGINS: {v}")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Variables extra en .env se ignoran sin lanzar error
    )


@lru_cache
def get_settings() -> Settings:
    """
    Retorna una instancia única y cacheada de Settings (patrón Singleton).

    El decorador @lru_cache garantiza que el archivo .env se lea del disco
    una sola vez durante todo el ciclo de vida de la aplicación.
    Al usar Depends(get_settings) en los endpoints, FastAPI permite
    sobreescribir la configuración fácilmente en tests automatizados.
    """
    return Settings()


# Instancia de acceso directo (para uso fuera del sistema de inyección de dependencias)
settings = get_settings()
