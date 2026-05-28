"""
Módulo de Loaders para el Arquitecto Senior RAG.
Cada loader se encarga de procesar un tipo específico de archivo.
"""

from .code_loader import cargar_codigo_fuente
from .diagram_loader import cargar_diagramas
from .data_dictionary_loader import cargar_diccionarios_datos
from .docs_loader import cargar_documentacion
from .infra_loader import cargar_infraestructura

__all__ = [
    "cargar_codigo_fuente",
    "cargar_diagramas",
    "cargar_diccionarios_datos",
    "cargar_documentacion",
    "cargar_infraestructura",
]
