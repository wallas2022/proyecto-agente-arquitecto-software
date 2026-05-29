"""
Endpoints REST para la gestion de usuarios y autenticacion.
"""

import hashlib
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.modelos import Usuario

router = APIRouter()

# Secret key para JWT (en produccion debe venir de variables de entorno)
SECRET_KEY = "cambiar_en_produccion"


def hashear_password(password: str) -> str:
    """
    Genera un hash SHA-256 con sal para la contrasena.
    En produccion deberia usarse bcrypt o argon2.
    """
    salt = "mercashop_salt_2026"
    return hashlib.sha256((password + salt).encode()).hexdigest()


def verificar_password(password: str, hash_guardado: str) -> bool:
    """Verifica que una contrasena coincida con su hash."""
    return hashear_password(password) == hash_guardado


@router.post("/registro")
async def registrar_usuario(datos: dict, db: AsyncSession = Depends(get_db)):
    """
    Registra un nuevo usuario.
    Reglas de negocio:
    - El email debe ser unico en el sistema.
    - La contrasena debe tener minimo 8 caracteres.
    - El email debe contener '@'.
    """
    email = datos.get("email", "")
    password = datos.get("password", "")

    # Validaciones
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Email invalido")
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="La contrasena debe tener al menos 8 caracteres")

    # Verificar email unico
    existente = await db.execute(select(Usuario).where(Usuario.email == email))
    if existente.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="El email ya esta registrado")

    nuevo = Usuario(
        email=email,
        password_hash=hashear_password(password),
        nombre=datos.get("nombre"),
        apellido=datos.get("apellido"),
        telefono=datos.get("telefono"),
        direccion=datos.get("direccion"),
    )
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return {"id": nuevo.id, "email": nuevo.email, "mensaje": "Usuario registrado exitosamente"}


@router.post("/login")
async def login(credenciales: dict, db: AsyncSession = Depends(get_db)):
    """Autentica un usuario y devuelve un token de sesion."""
    email = credenciales.get("email")
    password = credenciales.get("password")

    result = await db.execute(select(Usuario).where(Usuario.email == email))
    usuario = result.scalar_one_or_none()

    if not usuario or not verificar_password(password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    if not usuario.activo:
        raise HTTPException(status_code=403, detail="Usuario desactivado")

    # En produccion usar JWT real
    token = hashlib.sha256(f"{usuario.id}{datetime.utcnow()}{SECRET_KEY}".encode()).hexdigest()

    return {
        "token": token,
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "expira_en": (datetime.utcnow() + timedelta(hours=24)).isoformat()
    }


@router.get("/{usuario_id}")
async def obtener_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene los datos de un usuario por su ID."""
    result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # No devolver el hash de la contrasena
    return {
        "id": usuario.id,
        "email": usuario.email,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "telefono": usuario.telefono,
        "direccion": usuario.direccion,
        "fecha_registro": usuario.fecha_registro
    }
