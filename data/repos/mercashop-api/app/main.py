"""
MercaShop API - Sistema de gestion de tienda online.
Aplicacion principal con FastAPI.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import productos, usuarios, pedidos, pagos
from app.database import init_db

app = FastAPI(
    title="MercaShop API",
    description="API REST para la gestion de la tienda online MercaShop",
    version="1.0.0"
)

# Configuracion CORS para el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://mercashop.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(productos.router, prefix="/api/productos", tags=["Productos"])
app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(pedidos.router, prefix="/api/pedidos", tags=["Pedidos"])
app.include_router(pagos.router, prefix="/api/pagos", tags=["Pagos"])


@app.on_event("startup")
async def startup_event():
    """Inicializa la base de datos al arrancar la aplicacion."""
    await init_db()


@app.get("/")
async def root():
    return {
        "mensaje": "Bienvenido a MercaShop API",
        "version": "1.0.0",
        "documentacion": "/docs"
    }


@app.get("/health")
async def health_check():
    """Endpoint de salud para verificar que el servicio esta activo."""
    return {"status": "healthy"}
