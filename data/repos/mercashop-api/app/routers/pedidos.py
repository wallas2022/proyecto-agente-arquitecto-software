"""
Endpoints REST para la gestion de pedidos.
Implementa la logica de creacion de pedidos, calculo de totales
y validacion de stock.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.modelos import Pedido, DetallePedido, Producto, Usuario

router = APIRouter()

# Tasa de impuestos aplicada a todos los pedidos
TASA_IMPUESTOS = 0.12  # 12% IVA Guatemala

# Umbral para envio gratuito
UMBRAL_ENVIO_GRATIS = 500.00
COSTO_ENVIO_ESTANDAR = 35.00


def calcular_total_pedido(subtotal: float) -> dict:
    """
    Calcula el total final de un pedido aplicando:
    - Impuestos (IVA 12%)
    - Costo de envio (gratis si subtotal > 500)
    Regla de negocio clave del sistema MercaShop.
    """
    impuestos = subtotal * TASA_IMPUESTOS
    envio = 0 if subtotal >= UMBRAL_ENVIO_GRATIS else COSTO_ENVIO_ESTANDAR
    total = subtotal + impuestos + envio
    return {
        "subtotal": round(subtotal, 2),
        "impuestos": round(impuestos, 2),
        "envio": round(envio, 2),
        "total": round(total, 2),
    }


@router.post("/")
async def crear_pedido(datos: dict, db: AsyncSession = Depends(get_db)):
    """
    Crea un nuevo pedido. Flujo completo:
    1. Valida que el usuario exista.
    2. Valida que cada producto exista y tenga stock suficiente.
    3. Calcula subtotal, impuestos y envio.
    4. Descuenta stock de cada producto.
    5. Crea el pedido con estado 'pendiente' (espera pago).

    El campo total_pedido se calcula a partir de los detalles
    y NO debe enviarse desde el cliente para evitar manipulacion.
    """
    usuario_id = datos.get("usuario_id")
    items = datos.get("items", [])  # [{producto_id, cantidad}]
    direccion_envio = datos.get("direccion_envio")

    if not items:
        raise HTTPException(status_code=400, detail="El pedido debe tener al menos un item")
    if not direccion_envio:
        raise HTTPException(status_code=400, detail="La direccion de envio es obligatoria")

    # Validar usuario
    user_result = await db.execute(select(Usuario).where(Usuario.id == usuario_id))
    if not user_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    subtotal = 0.0
    detalles_a_crear = []

    # Validar productos y calcular subtotal
    for item in items:
        prod_id = item.get("producto_id")
        cantidad = item.get("cantidad", 0)

        if cantidad <= 0:
            raise HTTPException(status_code=400, detail=f"Cantidad invalida para producto {prod_id}")

        prod_result = await db.execute(select(Producto).where(Producto.id == prod_id))
        producto = prod_result.scalar_one_or_none()
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {prod_id} no existe")
        if producto.stock < cantidad:
            raise HTTPException(
                status_code=400,
                detail=f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}"
            )

        sub_item = producto.precio * cantidad
        subtotal += sub_item
        detalles_a_crear.append({
            "producto": producto,
            "cantidad": cantidad,
            "precio_unitario": producto.precio,
            "subtotal": sub_item,
        })

    # Calcular totales con la logica de negocio
    calculo = calcular_total_pedido(subtotal)

    # Crear el pedido
    nuevo_pedido = Pedido(
        usuario_id=usuario_id,
        total_pedido=calculo["total"],
        direccion_envio=direccion_envio,
        estado="pendiente"
    )
    db.add(nuevo_pedido)
    await db.flush()  # Para obtener el ID antes del commit

    # Crear detalles y descontar stock
    for d in detalles_a_crear:
        detalle = DetallePedido(
            pedido_id=nuevo_pedido.id,
            producto_id=d["producto"].id,
            cantidad=d["cantidad"],
            precio_unitario=d["precio_unitario"],
            subtotal=d["subtotal"],
        )
        db.add(detalle)
        d["producto"].stock -= d["cantidad"]  # Descontar stock

    await db.commit()
    await db.refresh(nuevo_pedido)

    return {
        "pedido_id": nuevo_pedido.id,
        "estado": nuevo_pedido.estado,
        **calculo
    }


@router.get("/{pedido_id}")
async def obtener_pedido(pedido_id: int, db: AsyncSession = Depends(get_db)):
    """Obtiene los detalles de un pedido."""
    result = await db.execute(select(Pedido).where(Pedido.id == pedido_id))
    pedido = result.scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return pedido


@router.put("/{pedido_id}/estado")
async def cambiar_estado_pedido(pedido_id: int, nuevo_estado: str, db: AsyncSession = Depends(get_db)):
    """
    Cambia el estado de un pedido siguiendo la maquina de estados:
    pendiente -> pagado -> enviado -> entregado
    Cualquier estado puede ir a 'cancelado'.
    """
    transiciones_validas = {
        "pendiente": ["pagado", "cancelado"],
        "pagado": ["enviado", "cancelado"],
        "enviado": ["entregado"],
        "entregado": [],
        "cancelado": [],
    }

    result = await db.execute(select(Pedido).where(Pedido.id == pedido_id))
    pedido = result.scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")

    if nuevo_estado not in transiciones_validas.get(pedido.estado, []):
        raise HTTPException(
            status_code=400,
            detail=f"No se puede pasar de '{pedido.estado}' a '{nuevo_estado}'"
        )

    pedido.estado = nuevo_estado
    await db.commit()
    return {"pedido_id": pedido.id, "estado_nuevo": pedido.estado}
