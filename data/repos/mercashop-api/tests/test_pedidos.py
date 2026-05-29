"""
Tests unitarios para la logica de pedidos de MercaShop.
"""

import pytest
from app.routers.pedidos import calcular_total_pedido, TASA_IMPUESTOS, UMBRAL_ENVIO_GRATIS


def test_calcular_total_sin_envio_gratis():
    """Pedido pequeno: lleva costo de envio."""
    resultado = calcular_total_pedido(100.0)
    assert resultado["subtotal"] == 100.0
    assert resultado["impuestos"] == 12.0  # 12% de 100
    assert resultado["envio"] == 35.0  # costo estandar
    assert resultado["total"] == 147.0


def test_calcular_total_con_envio_gratis():
    """Pedido grande: envio gratuito por superar umbral."""
    resultado = calcular_total_pedido(600.0)
    assert resultado["envio"] == 0
    assert resultado["total"] == 672.0  # 600 + 72 IVA


def test_pedido_exacto_umbral_es_envio_gratis():
    """En el umbral exacto, el envio ya es gratis."""
    resultado = calcular_total_pedido(UMBRAL_ENVIO_GRATIS)
    assert resultado["envio"] == 0
