import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from musica_api.config import get_settings, validate_settings
from musica_api.database import create_db_and_tables, engine
from musica_api.routers import usuarios, canciones, favoritos

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    validate_settings()
    create_db_and_tables()
    yield
    print("Cerrando aplicación...")


# Instancia principal de FastAPI
app = FastAPI(
    title=settings.app_name,
    description="API RESTful para gestionar usuarios, canciones y favoritos",
    version=settings.app_version,
    lifespan=lifespan,
    contact={
        "name": "Juan Camilo Díaz",
        "email": "juan@example.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware opcional para logging de tiempos de respuesta
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Manejador de errores personalizado
@app.exception_handler(Exception)
async def custom_global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor", "error": str(exc)},
    )


# Inclusión de routers
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(canciones.router, prefix="/api/canciones", tags=["Canciones"])
app.include_router(favoritos.router, prefix="/api/favoritos", tags=["Favoritos"])


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz de la API."""
    return {
        "message": f"Bienvenido a {settings.app_name}",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint para monitoreo."""
    db_status = "ok"
    try:
        with Session(engine) as session:
            session.exec(select(1))
    except Exception:
        db_status = "error"

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "database": db_status,
        "environment": settings.environment,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )