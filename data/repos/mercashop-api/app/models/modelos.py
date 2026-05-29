"""
Modelos ORM de SQLAlchemy para MercaShop.
Define las tablas principales del sistema.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Usuario(Base):
    """Tabla de usuarios registrados en la tienda."""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(20))
    direccion = Column(Text)
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    pedidos = relationship("Pedido", back_populates="usuario")


class Producto(Base):
    """Tabla de productos disponibles en la tienda."""
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    categoria = Column(String(80), index=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)


class Pedido(Base):
    """Tabla de pedidos realizados por usuarios."""
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_pedido = Column(DateTime, default=datetime.utcnow)
    total_pedido = Column(Float, nullable=False)
    estado = Column(String(30), default="pendiente")  # pendiente, pagado, enviado, entregado, cancelado
    direccion_envio = Column(Text, nullable=False)

    usuario = relationship("Usuario", back_populates="pedidos")
    detalles = relationship("DetallePedido", back_populates="pedido")
    pago = relationship("Pago", back_populates="pedido", uselist=False)


class DetallePedido(Base):
    """Tabla de items de cada pedido."""
    __tablename__ = "detalle_pedidos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    pedido = relationship("Pedido", back_populates="detalles")


class Pago(Base):
    """Tabla de pagos asociados a pedidos."""
    __tablename__ = "pagos"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), unique=True, nullable=False)
    metodo_pago = Column(String(50), nullable=False)  # tarjeta, paypal, transferencia
    monto = Column(Float, nullable=False)
    estado_pago = Column(String(30), default="pendiente")  # pendiente, completado, fallido, reembolsado
    fecha_pago = Column(DateTime)
    referencia_externa = Column(String(200))  # ID del proveedor de pagos

    pedido = relationship("Pedido", back_populates="pago")
