from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.router import router as admin_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.db.database import init_db
from app.services import key_rotation_service

# Swagger y ReDoc se ocultan automáticamente fuera de development.
# En staging/production, la documentación no es accesible públicamente.
_docs_url = "/docs" if settings.DEBUG or settings.ENVIRONMENT == "development" else None
_redoc_url = "/redoc" if settings.DEBUG or settings.ENVIRONMENT == "development" else None


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    key_rotation_service.seed_from_env_if_empty()
    yield


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

---

### 🛠️ Panel de Administración (`/admin`)

Fuera de esta API versionada (es HTML, no JSON) vive un panel interno protegido con
**HTTP Basic Auth** (usuario/clave definidos en `ADMIN_USERNAME` / `ADMIN_PASSWORD` del `.env`),
por eso no aparece como path en este esquema OpenAPI. Permite:

* Visualizar el consumo de Google Gemini en tiempo real: requests y tokens usados vs. los
  límites de la capa gratuita (**RPM**, **TPM**, **RPD**), por cada API key configurada.
* Cargar hasta **3 API keys** de Gemini (cifradas en reposo con Fernet), cada una con sus
  propios umbrales de RPM/TPM/RPD/TPD.
* **Rotación automática**: cuando la key activa se acerca a cualquiera de sus umbrales, el
  backend rota solo a la siguiente key disponible antes de la próxima llamada a Gemini —
  sin caídas de servicio ni intervención manual.

Acceso: `http://<host>:<puerto>/admin` (solo en el entorno donde se despliegue; no depende
de `ENVIRONMENT`, siempre requiere las credenciales de admin).
""",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=_docs_url,
    redoc_url=_redoc_url,
    debug=settings.DEBUG,
    lifespan=lifespan,
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

# Panel de administración (HTML interno, protegido con HTTP Basic Auth)
app.include_router(admin_router, prefix="/admin")


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
