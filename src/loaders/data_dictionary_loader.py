"""
Loader para Diccionarios de Datos.
Soporta:
- Excel (.xlsx): lee todas las hojas.
- CSV (.csv): lee como tabla.
- JSON (.json): convierte a texto estructurado.
"""

import os
import json
import pandas as pd
from pathlib import Path
from langchain_core.documents import Document


def leer_excel(ruta_archivo: str) -> list[Document]:
    """
    Lee un archivo Excel y genera un documento por cada hoja.
    """
    documentos = []
    try:
        # Leer todas las hojas
        excel_file = pd.ExcelFile(ruta_archivo)

        for hoja in excel_file.sheet_names:
            df = pd.read_excel(ruta_archivo, sheet_name=hoja)

            if df.empty:
                continue

            # Convertir a texto legible para el LLM
            texto = f"DICCIONARIO DE DATOS - Archivo: {os.path.basename(ruta_archivo)}\n"
            texto += f"Hoja: {hoja}\n"
            texto += f"Columnas: {', '.join(df.columns.astype(str))}\n\n"
            texto += "=== CONTENIDO DE LA TABLA ===\n"
            texto += df.to_string(index=False, max_rows=200)

            documento = Document(
                page_content=texto,
                metadata={
                    "fuente": ruta_archivo,
                    "tipo": "diccionario_datos_excel",
                    "hoja": hoja,
                    "nombre_archivo": os.path.basename(ruta_archivo),
                    "columnas": ", ".join(df.columns.astype(str)),
                }
            )
            documentos.append(documento)

    except Exception as e:
        print(f"  ⚠️  Error leyendo Excel {ruta_archivo}: {e}")

    return documentos


def leer_csv(ruta_archivo: str) -> Document:
    """
    Lee un archivo CSV.
    """
    try:
        df = pd.read_csv(ruta_archivo, encoding="utf-8")

        if df.empty:
            return None

        texto = f"DICCIONARIO DE DATOS - Archivo CSV: {os.path.basename(ruta_archivo)}\n"
        texto += f"Columnas: {', '.join(df.columns.astype(str))}\n\n"
        texto += "=== CONTENIDO ===\n"
        texto += df.to_string(index=False, max_rows=200)

        return Document(
            page_content=texto,
            metadata={
                "fuente": ruta_archivo,
                "tipo": "diccionario_datos_csv",
                "nombre_archivo": os.path.basename(ruta_archivo),
                "columnas": ", ".join(df.columns.astype(str)),
            }
        )
    except Exception as e:
        print(f"  ⚠️  Error leyendo CSV {ruta_archivo}: {e}")
        return None


def leer_json(ruta_archivo: str) -> Document:
    """
    Lee un archivo JSON y lo convierte a texto.
    """
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convertir a texto formateado e indentado
        texto = f"DICCIONARIO DE DATOS - Archivo JSON: {os.path.basename(ruta_archivo)}\n\n"
        texto += json.dumps(data, indent=2, ensure_ascii=False)

        return Document(
            page_content=texto,
            metadata={
                "fuente": ruta_archivo,
                "tipo": "diccionario_datos_json",
                "nombre_archivo": os.path.basename(ruta_archivo),
            }
        )
    except Exception as e:
        print(f"  ⚠️  Error leyendo JSON {ruta_archivo}: {e}")
        return None


def cargar_diccionarios_datos(carpeta: str) -> list[Document]:
    """
    Carga todos los diccionarios de datos de una carpeta.
    """
    documentos = []

    if not os.path.exists(carpeta):
        print(f"  ⚠️  La carpeta {carpeta} no existe.")
        return documentos

    print(f"  🔍 Escaneando diccionarios de datos en: {carpeta}")

    for raiz, _, archivos in os.walk(carpeta):
        for archivo in archivos:
            ruta = os.path.join(raiz, archivo)
            extension = Path(archivo).suffix.lower()

            if extension == ".xlsx":
                documentos.extend(leer_excel(ruta))
            elif extension == ".csv":
                doc = leer_csv(ruta)
                if doc:
                    documentos.append(doc)
            elif extension == ".json":
                doc = leer_json(ruta)
                if doc:
                    documentos.append(doc)

    print(f"  ✅ Diccionarios de datos: {len(documentos)} documentos cargados")
    return documentos


# ===== Test =====
if __name__ == "__main__":
    docs = cargar_diccionarios_datos("data/diccionarios")
    print(f"\nTotal diccionarios: {len(docs)}")
    if docs:
        print("\nPrimer documento (muestra):")
        print(docs[0].page_content[:500])
