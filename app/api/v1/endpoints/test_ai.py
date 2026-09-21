from fastapi import APIRouter, Depends, HTTPException

from app.core.config import Settings, get_settings
from app.services.gemini_service import gemini_service
from app.services.key_rotation_service import AllKeysExhaustedError

router = APIRouter()


@router.post(
    "/test-gemini",
    summary="Validar conexión con Google Gemini API",
    response_description="Resultado de la prueba de conectividad y respuesta del modelo de IA",
)
async def test_gemini_connection(settings: Settings = Depends(get_settings)):
    """
    ## Prueba de Conectividad con Gemini API (Semana 0)

    Envía un prompt de verificación a la API de **Google Gemini** utilizando
    comunicación asíncrona nativa (client.aio) y el modelo configurado
    en la variable de entorno GEMINI_MODEL. La API key usada se obtiene del
    pool de keys gestionado desde el [panel de administración](/admin),
    con rotación automática entre hasta 3 keys.

    ### Respuestas posibles:
    - **200 OK**: La key activa es válida y Gemini devolvió respuesta exitosa.
    - **400 Bad Request**: No hay ninguna API key de Gemini configurada (agregar una desde `/admin`).
    - **429 Too Many Requests**: Las 3 keys alcanzaron su límite (RPM/TPM/RPD) configurado.
    - **500 Internal Server Error**: Error de red, cuota excedida o autenticación inválida con Google.
    """
    try:
        result = await gemini_service.ping_connection()
        return result
    except AllKeysExhaustedError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al comunicar con Gemini API: {str(e)}",
        )
