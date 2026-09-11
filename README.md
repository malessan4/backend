# 🧠 Asistente de Accesibilidad para Contenidos Educativos - Backend
> **Innova Lab** | Agencia de Habilidades para el Futuro  
> *Herramienta de Inteligencia Artificial para la creación y adaptación de contenidos educativos accesibles.*

---

## 📋 Descripción del Proyecto

Los materiales educativos digitales suelen presentar barreras de accesibilidad relacionadas con su estructura, complejidad del lenguaje, legibilidad y ausencia de alternativas textuales en imágenes.

Este backend provee la API REST que impulsa el producto:
- **Escaneo y diagnóstico:** Combina reglas heurísticas automáticas con el análisis semántico de **Google Gemini API**.
- **Asistencia a la adaptación:** Genera sugerencias (simplificación de textos, consignas paso a paso, textos alternativos para imágenes) sin reemplazar el criterio pedagógico del docente.
- **Control docente:** Cada propuesta de adaptación puede ser aceptada, editada o descartada por el docente antes de exportar el material final.

---

## 🏛️ Arquitectura del Software y Decisiones Técnicas

El backend fue diseñado bajo una **arquitectura en capas desacopladas (Clean Architecture simplificada)**, asegurando escalabilidad, mantenibilidad y facilidad de prueba:

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/        # Capa de Controladores HTTP (Health, AI, Documentos)
│   │       └── router.py         # Versionado y unificación de rutas v1
│   ├── core/
│   │   └── config.py             # Configuración centralizada y tipada (Pydantic Settings)
│   ├── services/
│   │   └── gemini_service.py     # Capa de Negocio e Integración con Gemini API
│   └── main.py                   # Instanciación de FastAPI, Middlewares y OpenAPI
├── .env                          # Variables sensibles locales (IGNORADO en Git)
├── .env.example                  # Plantilla pública de variables requeridas
├── .gitignore                    # Reglas de exclusión de seguridad y entorno
├── requirements.txt              # Dependencias fijadas del proyecto
└── README.md                     # Documentación general de arquitectura y ejecución
```

### 💡 Justificación de Decisiones Técnicas:

1. **FastAPI como Framework Web:**
   - **Asincronía nativa (sync / await):** Las llamadas a modelos de lenguaje (LLMs) y el procesamiento de documentos generan latencia de I/O. La arquitectura asíncrona de FastAPI evita que el servidor se bloquee, permitiendo atender múltiples peticiones concurrentes.
   - **Validación con Pydantic:** Validación estricta de esquemas de entrada y salida, asegurando contratos de datos claros con el equipo de Frontend y reduciendo errores en tiempo de ejecución.
2. **Documentación OpenAPI Automática (Swagger UI):**
   - Disponibilidad inmediata de documentación interactiva en /docs y /redoc sin necesidad de mantener colecciones manuales en Postman.
3. **Capa de Servicios Aislada (services/):**
   - La lógica de integración con Google Gemini está desacoplada de los controladores HTTP. Si se cambia de modelo o de proveedor en futuros sprints, los endpoints permanecen intactos.
4. **Manejo Seguro de Secretos y Configuración (pydantic-settings):**
   - Ninguna credencial sensible está hardcodeada. La API Key se lee dinámicamente desde variables de entorno (.env), con respaldo de una plantilla .env.example.
5. **Políticas de CORS Preconfiguradas:**
   - Configuración explícita de orígenes seguros (localhost:3000, localhost:5173) para evitar problemas de bloqueo de peticiones cruzadas durante el desarrollo con React/Vite/Next.js.

---

## 📖 Documentación de la API (Swagger y ReDoc)

FastAPI autogenera dos interfaces de documentación interactiva:

* **Swagger UI (Pruebas interactivas):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
  *Permite probar cada endpoint en vivo haciendo clic en **"Try it out"** y luego en **"Execute"**.*
* **ReDoc (Documentación técnica limpia):** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 📡 Endpoints Implementados (Semana 0)

| Método | Endpoint | Descripción | Estado |
| :--- | :--- | :--- | :--- |
| GET | / | Bienvenida y enlaces a la documentación | ✅ Operativo |
| GET | /api/v1/health | Chequeo de estado y versión del backend | ✅ Operativo |
| POST | /api/v1/ai/test-gemini | Validación de conectividad y credenciales con Google Gemini | ✅ Operativo |

---

## 🛠️ Guía de Puesta en Marcha Local

### 1. Requisitos Previos
- Python 3.10 o superior (recomendado 3.11 a 3.13).
- Obtener una API Key gratuita de Gemini en [Google AI Studio](https://aistudio.google.com/).

### 2. Clonar el repositorio y configurar el entorno
`powershell
# 1. Crear el entorno virtual
py -m venv venv

# 2. Activar el entorno virtual (Windows PowerShell)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1

# 3. Instalar las dependencias
pip install -r requirements.txt
`

### 3. Configurar variables de entorno
Copiar la plantilla .env.example para crear el archivo local .env:
`powershell
Copy-Item .env.example .env
`
Editar .env y configurar la clave:
`env
GEMINI_API_KEY=tu_api_key_real_de_gemini
`

### 4. Ejecutar el servidor de desarrollo
`powershell
uvicorn app.main:app --reload
`
Acceder a la documentación interactiva en: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**.

---

## 🗺️ Roadmap de Backend (Plan de 12 Semanas)

- [x] **Semana 0 (Sprint Planning):** Setup del entorno, arquitectura modular, configuración de CORS y validación de Gemini API.
- [ ] **Semana 1-2 (Sprint 1 - Exploración):** Pipeline de procesamiento de texto y PDFs (PyMuPDF), primeras pruebas de análisis con Gemini.
- [ ] **Semana 3-4 (Sprint 2 - Ideación):** Motor de reglas automáticas + cálculo del puntaje orientativo de accesibilidad (0-100).
- [ ] **Semana 5-6 (Sprint 3 - Desarrollo):** Generación de adaptaciones con IA (lenguaje claro, consignas en pasos, descripciones de imágenes).
- [ ] **Semana 7-8 (Sprint 4 - Consolidación):** Consolidación de informe final y exportación del material adaptado.
- [ ] **Semana 9-10 (Sprint 5 - Iteración):** Optimización de latencias, prompts estructurados y mitigación de falsos positivos.
- [ ] **Semana 11-12 (Sprint 6 - Cierre):** Entorno estable y validaciones para el **Demo Day**.
