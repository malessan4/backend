from google import genai

from app.core.config import settings


class GeminiService:
    """
    Capa de servicio para la integración con Google Gemini API.

    Encapsula toda la lógica de comunicación con el modelo de lenguaje,
    manteniendo los endpoints desacoplados del proveedor de IA.
    Si en el futuro se cambia de modelo o proveedor, solo se modifica esta clase.
    """

    def __init__(self):
        self._client: genai.Client | None = None

    @property
    def client(self) -> genai.Client:
        """
        Inicializa el cliente de Gemini de forma lazy (solo cuando se necesita).
        Usa get_secret_value() para extraer el string real desde SecretStr de forma segura.
        """
        api_key = settings.GEMINI_API_KEY.get_secret_value()

        if not api_key or api_key == "tu_api_key_aqui":
            raise ValueError(
                "GEMINI_API_KEY no configurada. "
                "Por favor agrega tu clave real en el archivo .env."
            )
        if self._client is None:
            self._client = genai.Client(api_key=api_key)
        return self._client

    async def ping_connection(self) -> dict:
        """
        Envía un prompt mínimo a Gemini para validar credenciales y conectividad.
        Usa client.aio para comunicación asíncrona no bloqueante.
        """
        model = settings.GEMINI_MODEL
        response = await self.client.aio.models.generate_content(
            model=model,
            contents="Responde únicamente con la palabra: 'CONECTADO'.",
        )
        return {
            "status": "success",
            "environment": settings.ENVIRONMENT,
            "model": model,
            "response": response.text.strip(),
        }


gemini_service = GeminiService()
