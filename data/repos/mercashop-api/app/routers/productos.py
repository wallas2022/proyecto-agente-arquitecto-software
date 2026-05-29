"""
Endpoints REST para la gestion de productos en MercaShop.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.modelos import Producto

router = APIRouter()


@router.get("/")
async def listar_productos(
    categoria: str = None,
    activos: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos los productos. Filtra por categoria y por estado activo.
    """
    query = select(Producto)
    if activos:
        query = query.where(Producto.activo == True)
    if categoria:
        query = query.where(Producto.categoria == categoria)
    result = await db.execute(query)
    productos = result.scalars().all()
    return productos


@router.get("/{producto_id}")
async def obtener_producto(producto_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene un producto por su ID."""
    result = await db.execute(select(Producto).where(Producto.id == producto_id))
    producto = result.scalar_one_or_none()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.post("/")
async def crear_producto(datos: dict, db: AsyncSession = Depends(get_db)):
    """
    Crea un nuevo producto.
    Reglas de negocio:
    - El SKU debe ser unico.
    - El precio debe ser positivo.
    - El stock inicial no puede ser negativo.
    """
    if datos.get("precio", 0) <= 0:
        raise HTTPException(status_code=400, detail="El precio debe ser mayor a 0")
    if datos.get("stock", 0) < 0:
        raise HTTPException(status_code=400, detail="El stock no puede ser negativo")

    nuevo = Producto(**datos)
    db.add(nuevo)
    await db.commit()
    await db.refresh(nuevo)
    return nuevo


@router.put("/{producto_id}/stock")
async def actualizar_stock(producto_id: int, cantidad: int, db: AsyncSession = Depends(get_db)):
    """Actualiza el stock de un producto (suma o resta segun el signo)."""
    result = await db.execute(select(Producto).where(Producto.id == producto_id))
    producto = result.scalar_one_or_none()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    nuevo_stock = producto.stock + cantidad
    if nuevo_stock < 0:
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    producto.stock = nuevo_stock
    await db.commit()
    return {"id": producto.id, "stock_actual": producto.stock}
