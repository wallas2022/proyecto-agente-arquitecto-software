"""
Loader para Documentación Técnica.
Soporta:
- Markdown (.md): manuales, READMEs, especificaciones.
- PDF (.pdf): documentos técnicos, manuales escaneados o digitales.
"""

import os
from pathlib import Path
import pdfplumber
from langchain_core.documents import Document


def leer_markdown(ruta_archivo: str) -> Document:
    """
    Lee un archivo Markdown.
    """
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()

        if not contenido.strip():
            return None

        return Document(
            page_content=contenido,
            metadata={
                "fuente": ruta_archivo,
                "tipo": "documentacion_markdown",
                "nombre_archivo": os.path.basename(ruta_archivo),
            }
        )
    except Exception as e:
        print(f"  ⚠️  Error leyendo Markdown {ruta_archivo}: {e}")
        return None


def leer_pdf(ruta_archivo: str) -> list[Document]:
    """
    Lee un archivo PDF y crea un documento por cada página.
    Usar páginas separadas mejora la precisión del retrieval.
    """
    documentos = []
    try:
        with pdfplumber.open(ruta_archivo) as pdf:
            for num_pagina, pagina in enumerate(pdf.pages, start=1):
                texto = pagina.extract_text()

                if texto and texto.strip():
                    doc = Document(
                        page_content=texto,
                        metadata={
                            "fuente": ruta_archivo,
                            "tipo": "documentacion_pdf",
                            "nombre_archivo": os.path.basename(ruta_archivo),
                            "pagina": num_pagina,
                            "total_paginas": len(pdf.pages),
                        }
                    )
                    documentos.append(doc)
    except Exception as e:
        print(f"  ⚠️  Error leyendo PDF {ruta_archivo}: {e}")

    return documentos


def cargar_documentacion(carpeta: str) -> list[Document]:
    """
    Carga toda la documentación de una carpeta.
    """
    documentos = []

    if not os.path.exists(carpeta):
        print(f"  ⚠️  La carpeta {carpeta} no existe.")
        return documentos

    print(f"  🔍 Escaneando documentación en: {carpeta}")

    for raiz, _, archivos in os.walk(carpeta):
        for archivo in archivos:
            ruta = os.path.join(raiz, archivo)
            extension = Path(archivo).suffix.lower()

            if extension == ".md":
                doc = leer_markdown(ruta)
                if doc:
                    documentos.append(doc)
            elif extension == ".pdf":
                documentos.extend(leer_pdf(ruta))

    print(f"  ✅ Documentación: {len(documentos)} documentos cargados")
    return documentos


# ===== Test =====
if __name__ == "__main__":
    docs = cargar_documentacion("data/documentos")
    print(f"\nTotal docs: {len(docs)}")
    if docs:
        print("\nPrimer documento (muestra):")
        print(docs[0].page_content[:500])
