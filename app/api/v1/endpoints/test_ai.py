from fastapi import APIRouter, HTTPException
from app.services.gemini_service import gemini_service

router = APIRouter()


@router.post(
    "/test-gemini",
    summary="Validar conexión con Google Gemini API",
    response_description="Resultado de la prueba de conectividad y respuesta del modelo de IA"
)
async def test_gemini_connection():
    """
    ## Prueba de Conectividad con Gemini API (Semana 0)
    
    Envía un prompt de verificación a la API de **Google Gemini** utilizando
    comunicación asíncrona (client.aio) y el modelo configurado.
    
    ### Respuestas posibles:
    - **200 OK**: La API key es válida y Gemini devolvió una respuesta exitosa.
    - **400 Bad Request**: La variable GEMINI_API_KEY no fue configurada en .env.
    - **500 Internal Server Error**: Ocurrió un problema de red, cuota o autenticación con Google.
    """
    try:
        result = await gemini_service.ping_connection()
        return result
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=str(ve)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al comunicar con Gemini API: {str(e)}"
        )
