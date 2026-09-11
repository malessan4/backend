from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get(
    "/health",
    summary="Verificar estado del backend",
    response_description="Estado actual del servicio y versión de la API"
)
async def health_check():
    """
    ## Health Check del Sistema
    
    Verifica que el servidor de FastAPI esté en línea, respondiendo solicitudes
    y que la configuración básica del proyecto esté cargada correctamente.
    
    - **status**: 'online' si el servicio responde adecuadamente.
    - **project**: Nombre del proyecto configurado en el entorno.
    - **version**: Versión actual del release del backend.
    """
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": "0.1.0"
    }
