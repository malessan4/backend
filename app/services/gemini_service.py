from google import genai
from app.core.config import settings


class GeminiService:
    def __init__(self):
        self._client = None
        self.model_name = "gemini-2.5-flash"

    @property
    def client(self) -> genai.Client:
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "tu_api_key_aqui":
            raise ValueError(
                "GEMINI_API_KEY no configurada. Por favor agrega tu clave en el archivo .env."
            )
        if self._client is None:
            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return self._client

    async def ping_connection(self) -> dict:
        """Prueba de conexión rápida para validar credenciales y conectividad con Gemini."""
        client = self.client
        response = await client.aio.models.generate_content(
            model=self.model_name,
            contents="Responde únicamente con la palabra: 'CONECTADO'.",
        )
        return {
            "status": "success",
            "model": self.model_name,
            "response": response.text.strip(),
        }


gemini_service = GeminiService()
