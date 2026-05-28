"""
Script de prueba para los loaders de la Fase 2.
Ejecutar desde la raíz del proyecto:
    py src/test_loaders.py
"""

import sys
import os

# Agregar la carpeta src al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from loaders import (
    cargar_codigo_fuente,
    cargar_diagramas,
    cargar_diccionarios_datos,
    cargar_documentacion,
    cargar_infraestructura,
)


def main():
    print("=" * 70)
    print("🏗️  ARQUITECTO SENIOR RAG - Test de Loaders (Fase 2)")
    print("=" * 70)

    todos_documentos = []

    print("\n📦 1. CARGANDO CÓDIGO FUENTE...")
    docs_codigo = cargar_codigo_fuente("data/repos")
    todos_documentos.extend(docs_codigo)

    print("\n🏗️  2. CARGANDO DIAGRAMAS...")
    docs_diagramas = cargar_diagramas("data/diagramas")
    todos_documentos.extend(docs_diagramas)

    print("\n📊 3. CARGANDO DICCIONARIOS DE DATOS...")
    docs_datos = cargar_diccionarios_datos("data/diccionarios")
    todos_documentos.extend(docs_datos)

    print("\n📄 4. CARGANDO DOCUMENTACIÓN...")
    docs_docs = cargar_documentacion("data/documentos")
    todos_documentos.extend(docs_docs)

    print("\n🐳 5. CARGANDO INFRAESTRUCTURA...")
    docs_infra = cargar_infraestructura("data/infraestructura")
    todos_documentos.extend(docs_infra)

    print("\n" + "=" * 70)
    print(f"📊 RESUMEN TOTAL")
    print("=" * 70)
    print(f"  • Código fuente:    {len(docs_codigo)} documentos")
    print(f"  • Diagramas:        {len(docs_diagramas)} documentos")
    print(f"  • Diccionarios:     {len(docs_datos)} documentos")
    print(f"  • Documentación:    {len(docs_docs)} documentos")
    print(f"  • Infraestructura:  {len(docs_infra)} documentos")
    print(f"  ─────────────────────────────────")
    print(f"  🎯 TOTAL:           {len(todos_documentos)} documentos")
    print("=" * 70)

    if todos_documentos:
        print("\n✅ Fase 2 completada exitosamente.")
        print("\n📌 Ejemplo del primer documento cargado:")
        print(f"   Tipo: {todos_documentos[0].metadata.get('tipo')}")
        print(f"   Fuente: {todos_documentos[0].metadata.get('fuente')}")
        print(f"   Contenido (primeros 300 caracteres):")
        print(f"   {todos_documentos[0].page_content[:300]}...")
    else:
        print("\n⚠️  No se encontraron documentos.")
        print("   Coloca archivos de prueba en las carpetas de 'data/' y vuelve a ejecutar.")


if __name__ == "__main__":
    main()
