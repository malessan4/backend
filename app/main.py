from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
# 🧠 Asistente de Accesibilidad para Contenidos Educativos
*Innova Lab - Agencia de Habilidades para el Futuro*

API REST desarrollada con **FastAPI** y **Google Gemini API** para analizar, diagnosticar y adaptar materiales educativos digitales (PDF, texto), reduciendo barreras de accesibilidad y potenciando la labor pedagógica docente.

---

### 📌 Módulos de la API:
* **Health**: Verificación del estado del servidor y métricas de disponibilidad.
* **AI Integration**: Servicios de asistencia inteligente y comunicación con Google Gemini.
* *(Próximos Sprints)*: Extracción de documentos (PDF/Texto) y motor de diagnóstico de accesibilidad.
""",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuración de CORS para integración fluida con Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro unificado de rutas v1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"], summary="Punto de bienvenida de la API")
def root():
    """
    Ruta raíz informativa con accesos directos a la documentación y health check.
    """
    return {
        "message": "Bienvenido a la API de Accesibilidad Educativa (Innova Lab).",
        "docs_swagger": "/docs",
        "docs_redoc": "/redoc",
        "health": f"{settings.API_V1_STR}/health"
    }
