from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

# Swagger y ReDoc se ocultan automáticamente fuera de development.
# En staging/production, la documentación no es accesible públicamente.
_docs_url = "/docs" if settings.DEBUG or settings.ENVIRONMENT == "development" else None
_redoc_url = "/redoc" if settings.DEBUG or settings.ENVIRONMENT == "development" else None

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
# 🧠 Asistente de Accesibilidad para Contenidos Educativos
*Innova Lab - Agencia de Habilidades para el Futuro*

API REST desarrollada con **FastAPI** y **Google Gemini API** para analizar, diagnosticar
y adaptar materiales educativos digitales (PDF, texto), reduciendo barreras de accesibilidad
y potenciando la labor pedagógica docente.

---

### 📌 Módulos de la API:
* **Health**: Verificación del estado del servidor, entorno y versión.
* **AI Integration**: Servicios de asistencia inteligente con Google Gemini.
* *(Próximos Sprints)*: Extracción de documentos PDF/Texto y motor de diagnóstico de accesibilidad.
""",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    debug=settings.DEBUG,
)

# Middleware de CORS: permite peticiones desde los orígenes configurados en .env
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro unificado de rutas bajo el prefijo /api/v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"], summary="Punto de bienvenida de la API")
def root():
    """
    Ruta raíz informativa.
    Devuelve el estado del entorno activo y accesos directos a la documentación.
    """
    return {
        "message": "Bienvenido a la API de Accesibilidad Educativa (Innova Lab).",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "docs": "/docs" if _docs_url else "Documentación no disponible en este entorno.",
        "health": f"{settings.API_V1_STR}/health",
    }
