from google import genai

from app.core.config import settings
from app.services import key_rotation_service


class GeminiService:
    """
    Capa de servicio para la integración con Google Gemini API.

    Encapsula toda la lógica de comunicación con el modelo de lenguaje,
    manteniendo los endpoints desacoplados del proveedor de IA.
    Si en el futuro se cambia de modelo o proveedor, solo se modifica esta clase.
    """

    def __init__(self):
        self._clients: dict[int, genai.Client] = {}

    def _get_client(self) -> tuple[int, genai.Client]:
        """
        Obtiene la key activa (rotando si hace falta) y cachea un genai.Client
        por key_id para no recrearlo en cada llamada.
        """
        key_id, raw_key = key_rotation_service.get_active_client_key()
        if key_id not in self._clients:
            self._clients[key_id] = genai.Client(api_key=raw_key)
        return key_id, self._clients[key_id]

    async def ping_connection(self) -> dict:
        """
        Envía un prompt mínimo a Gemini para validar credenciales y conectividad.
        Usa client.aio para comunicación asíncrona no bloqueante.
        """
        model = settings.GEMINI_MODEL
        key_id, client = self._get_client()
        response = await client.aio.models.generate_content(
            model=model,
            contents="Responde únicamente con la palabra: 'CONECTADO'.",
        )
        if response.usage_metadata is not None:
            key_rotation_service.record_usage(key_id, response.usage_metadata)
        return {
            "status": "success",
            "environment": settings.ENVIRONMENT,
            "model": model,
            "response": response.text.strip(),
        }


gemini_service = GeminiService()
