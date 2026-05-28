"""
Módulo de Indexación (Fase 3).
Se encarga de:
1. Cargar todos los documentos usando los loaders.
2. Dividirlos en fragmentos (chunking) con estrategia adaptada por tipo.
3. Generar embeddings con un modelo multilingüe.
4. Almacenarlos en ChromaDB (base vectorial persistente).
"""

import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

import config
from loaders import (
    cargar_codigo_fuente,
    cargar_diagramas,
    cargar_diccionarios_datos,
    cargar_documentacion,
    cargar_infraestructura,
)


def cargar_todos_los_documentos() -> list:
    """
    Ejecuta todos los loaders y junta todos los documentos.
    """
    print("\n📚 Cargando todos los documentos de la base de conocimiento...")
    documentos = []

    documentos.extend(cargar_codigo_fuente(config.CARPETA_REPOS))
    documentos.extend(cargar_diagramas(config.CARPETA_DIAGRAMAS))
    documentos.extend(cargar_diccionarios_datos(config.CARPETA_DICCIONARIOS))
    documentos.extend(cargar_documentacion(config.CARPETA_DOCUMENTOS))
    documentos.extend(cargar_infraestructura(config.CARPETA_INFRAESTRUCTURA))

    print(f"\n  📦 Total de documentos cargados: {len(documentos)}")
    return documentos


def dividir_en_chunks(documentos: list) -> list:
    """
    Divide los documentos en fragmentos más pequeños.
    Usa RecursiveCharacterTextSplitter que respeta saltos de línea,
    párrafos y estructura del texto.
    """
    print("\n✂️  Dividiendo documentos en fragmentos (chunks)...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        # Separadores en orden de prioridad
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_documents(documentos)

    print(f"  ✅ {len(documentos)} documentos → {len(chunks)} fragmentos")
    return chunks


def crear_embeddings():
    """
    Crea el objeto de embeddings con el modelo multilingüe.
    La primera vez descarga el modelo (~470 MB).
    """
    print(f"\n🧠 Cargando modelo de embeddings: {config.MODELO_EMBEDDINGS}")
    print("   (La primera vez descarga el modelo, puede tardar unos minutos...)")

    embeddings = HuggingFaceEmbeddings(
        model_name=config.MODELO_EMBEDDINGS,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    print("  ✅ Modelo de embeddings listo")
    return embeddings


def construir_base_vectorial(chunks: list, embeddings, recrear: bool = True):
    """
    Construye (o recrea) la base vectorial ChromaDB con los fragmentos.

    Args:
        chunks: Lista de fragmentos de documentos.
        embeddings: Objeto de embeddings.
        recrear: Si True, borra la base anterior y crea una nueva.
    """
    print("\n💾 Construyendo base vectorial ChromaDB...")

    # Si se pide recrear, borrar la base anterior
    if recrear and os.path.exists(config.CARPETA_VECTORSTORE):
        print("  🗑️  Eliminando base vectorial anterior...")
        shutil.rmtree(config.CARPETA_VECTORSTORE, ignore_errors=True)

    # Crear la base vectorial y almacenar los chunks
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=config.NOMBRE_COLECCION,
        persist_directory=config.CARPETA_VECTORSTORE,
    )

    print(f"  ✅ Base vectorial creada con {len(chunks)} fragmentos")
    print(f"  📁 Guardada en: {config.CARPETA_VECTORSTORE}")
    return vectorstore


def indexar_todo():
    """
    Función principal: ejecuta todo el pipeline de indexación.
    """
    print("=" * 70)
    print("🏗️  ARQUITECTO SENIOR RAG - Indexación (Fase 3)")
    print("=" * 70)

    # 1. Cargar documentos
    documentos = cargar_todos_los_documentos()

    if not documentos:
        print("\n⚠️  No hay documentos para indexar.")
        print("   Coloca archivos en las carpetas de 'data/' y vuelve a ejecutar.")
        return None

    # 2. Dividir en chunks
    chunks = dividir_en_chunks(documentos)

    # 3. Crear embeddings
    embeddings = crear_embeddings()

    # 4. Construir base vectorial
    vectorstore = construir_base_vectorial(chunks, embeddings, recrear=True)

    print("\n" + "=" * 70)
    print("✅ INDEXACIÓN COMPLETADA")
    print("=" * 70)
    print(f"  • Documentos procesados: {len(documentos)}")
    print(f"  • Fragmentos indexados:  {len(chunks)}")
    print(f"  • Base vectorial en:     {config.CARPETA_VECTORSTORE}")
    print("=" * 70)

    return vectorstore


def cargar_base_vectorial_existente():
    """
    Carga una base vectorial ya creada (sin reindexar).
    Útil para la Fase 4 (consultas) sin tener que recrear todo.
    """
    if not os.path.exists(config.CARPETA_VECTORSTORE):
        print("⚠️  No existe una base vectorial. Ejecuta indexar_todo() primero.")
        return None

    embeddings = crear_embeddings()
    vectorstore = Chroma(
        collection_name=config.NOMBRE_COLECCION,
        embedding_function=embeddings,
        persist_directory=config.CARPETA_VECTORSTORE,
    )
    return vectorstore


# ===== Ejecutar indexación =====
if __name__ == "__main__":
    indexar_todo()
