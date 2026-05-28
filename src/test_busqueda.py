"""
Script de prueba para la búsqueda semántica (Fase 3).
Permite hacer consultas de prueba sobre la base vectorial
y ver qué fragmentos recupera.

Ejecutar desde la raíz del proyecto:
    py src/test_busqueda.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from indexer import cargar_base_vectorial_existente


def main():
    print("=" * 70)
    print("🔍 PRUEBA DE BÚSQUEDA SEMÁNTICA")
    print("=" * 70)

    # Cargar la base vectorial existente
    vectorstore = cargar_base_vectorial_existente()

    if vectorstore is None:
        print("\n❌ Primero debes indexar. Ejecuta: py src/indexer.py")
        return

    print("\n✅ Base vectorial cargada. Puedes hacer consultas de prueba.")
    print("   (Escribe 'salir' para terminar)\n")

    while True:
        consulta = input("🔎 Tu consulta: ").strip()

        if consulta.lower() in ["salir", "exit", "quit", ""]:
            print("\n👋 ¡Hasta luego!")
            break

        # Buscar los fragmentos más relevantes
        resultados = vectorstore.similarity_search_with_score(
            consulta,
            k=config.NUM_RESULTADOS
        )

        print(f"\n📋 {len(resultados)} fragmentos más relevantes:\n")

        for i, (doc, score) in enumerate(resultados, start=1):
            print(f"--- Resultado {i} (distancia: {score:.4f}) ---")
            print(f"  📁 Fuente: {doc.metadata.get('fuente', 'desconocida')}")
            print(f"  🏷️  Tipo: {doc.metadata.get('tipo', 'desconocido')}")
            print(f"  📝 Contenido: {doc.page_content[:250]}...")
            print()

        print("=" * 70)


if __name__ == "__main__":
    main()
