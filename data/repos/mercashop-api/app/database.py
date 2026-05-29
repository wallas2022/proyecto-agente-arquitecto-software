"""
Configuracion de la base de datos PostgreSQL para MercaShop.
Utiliza SQLAlchemy con soporte asincrono.
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# URL de conexion desde variables de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://mercashop_user:mercashop_pass@localhost:5432/mercashop_db"
)

# Motor asincrono de SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Generador de sesiones
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base para los modelos ORM
Base = declarative_base()


async def init_db():
    """Crea las tablas si no existen al iniciar la aplicacion."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency injection: provee una sesion de DB a los endpoints."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
