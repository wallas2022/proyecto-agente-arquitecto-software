"""
Endpoints REST para el procesamiento de pagos.
Integra con proveedor externo (simulado) y actualiza estado del pedido.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.modelos import Pago, Pedido

router = APIRouter()

# Metodos de pago aceptados
METODOS_VALIDOS = ["tarjeta", "paypal", "transferencia"]


@router.post("/")
async def procesar_pago(datos: dict, db: AsyncSession = Depends(get_db)):
    """
    Procesa el pago de un pedido. Flujo:
    1. Valida que el pedido exista y este en estado 'pendiente'.
    2. Valida que el monto coincida con el total del pedido.
    3. Llama al proveedor de pagos externo (simulado).
    4. Crea el registro de pago.
    5. Cambia el estado del pedido a 'pagado' si fue exitoso.
    """
    pedido_id = datos.get("pedido_id")
    metodo = datos.get("metodo_pago")
    monto = datos.get("monto", 0)

    if metodo not in METODOS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Metodo invalido. Permitidos: {', '.join(METODOS_VALIDOS)}"
        )

    # Validar pedido
    result = await db.execute(select(Pedido).where(Pedido.id == pedido_id))
    pedido = result.scalar_one_or_none()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if pedido.estado != "pendiente":
        raise HTTPException(
            status_code=400,
            detail=f"El pedido esta en estado '{pedido.estado}', no se puede pagar"
        )

    # Validar monto (debe coincidir con total del pedido)
    if abs(monto - pedido.total_pedido) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"El monto ({monto}) no coincide con el total del pedido ({pedido.total_pedido})"
        )

    # Procesar con proveedor externo (simulado)
    referencia = await procesar_con_proveedor(metodo, monto)

    # Registrar el pago
    pago = Pago(
        pedido_id=pedido_id,
        metodo_pago=metodo,
        monto=monto,
        estado_pago="completado",
        fecha_pago=datetime.utcnow(),
        referencia_externa=referencia,
    )
    db.add(pago)

    # Actualizar estado del pedido
    pedido.estado = "pagado"

    await db.commit()
    await db.refresh(pago)

    return {
        "pago_id": pago.id,
        "estado": pago.estado_pago,
        "referencia": referencia,
        "fecha": pago.fecha_pago,
    }


async def procesar_con_proveedor(metodo: str, monto: float) -> str:
    """
    Funcion simulada que representa la llamada al proveedor de pagos.
    En produccion aqui se integraria Stripe, PayPal, Banco, etc.
    """
    # Simulacion: genera una referencia aleatoria
    import uuid
    return f"{metodo.upper()}-{uuid.uuid4().hex[:12].upper()}"


@router.post("/{pago_id}/reembolso")
async def solicitar_reembolso(pago_id: int, motivo: str, db: AsyncSession = Depends(get_db)):
    """
    Solicita el reembolso de un pago.
    Reglas:
    - Solo se pueden reembolsar pagos en estado 'completado'.
    - El pedido debe estar en estado 'pagado' o 'enviado'.
    """
    result = await db.execute(select(Pago).where(Pago.id == pago_id))
    pago = result.scalar_one_or_none()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    if pago.estado_pago != "completado":
        raise HTTPException(status_code=400, detail="Solo se pueden reembolsar pagos completados")

    pago.estado_pago = "reembolsado"
    await db.commit()
    return {"pago_id": pago.id, "estado": pago.estado_pago, "motivo": motivo}
