"""
Loader para Diagramas de Arquitectura.
Soporta:
- Draw.io (.drawio y .xml): extrae nodos, conexiones y textos.
- Mermaid (.mmd, .mermaid): lee el código del diagrama.
"""

import os
from pathlib import Path
from lxml import etree
from langchain_core.documents import Document


def parsear_drawio(ruta_archivo: str) -> str:
    """
    Extrae el texto y la estructura de un archivo Draw.io.

    Args:
        ruta_archivo: Ruta al archivo .drawio o .xml

    Returns:
        Texto estructurado que describe el diagrama.
    """
    try:
        with open(ruta_archivo, "rb") as f:
            contenido = f.read()

        # Parsear el XML
        tree = etree.fromstring(contenido)

        # Buscar todas las celdas (nodos) del diagrama
        nodos = []
        conexiones = []

        # mxCell es el elemento principal de Draw.io
        for cell in tree.iter():
            tag = etree.QName(cell.tag).localname
            if tag == "mxCell":
                valor = cell.get("value", "")
                edge = cell.get("edge")  # Si es una conexión
                origen = cell.get("source")
                destino = cell.get("target")
                style = cell.get("style", "")

                if valor and valor.strip():
                    # Limpiar HTML básico que a veces tiene Draw.io
                    valor_limpio = (valor
                                    .replace("<br>", " ")
                                    .replace("<div>", " ")
                                    .replace("</div>", " ")
                                    .replace("&nbsp;", " ")
                                    .strip())

                    if edge == "1":
                        conexiones.append(f"Conexión: '{valor_limpio}' (de {origen} hacia {destino})")
                    else:
                        # Identificar tipo de elemento por estilo
                        tipo_elem = "Componente"
                        if "shape=cylinder" in style:
                            tipo_elem = "Base de Datos"
                        elif "shape=cloud" in style:
                            tipo_elem = "Servicio Cloud"
                        elif "ellipse" in style:
                            tipo_elem = "Evento/Estado"
                        elif "rhombus" in style:
                            tipo_elem = "Decisión"

                        nodos.append(f"{tipo_elem}: {valor_limpio}")

        # Armar texto descriptivo
        texto = f"DIAGRAMA DE ARQUITECTURA: {os.path.basename(ruta_archivo)}\n\n"
        texto += "=== COMPONENTES ===\n"
        texto += "\n".join(nodos) if nodos else "(Sin componentes detectados)"
        texto += "\n\n=== CONEXIONES Y FLUJOS ===\n"
        texto += "\n".join(conexiones) if conexiones else "(Sin conexiones detectadas)"

        return texto

    except Exception as e:
        print(f"  ⚠️  Error parseando {ruta_archivo}: {e}")
        return None


def parsear_mermaid(ruta_archivo: str) -> str:
    """
    Lee un archivo Mermaid (es texto plano).
    """
    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read()
        return f"DIAGRAMA MERMAID: {os.path.basename(ruta_archivo)}\n\n{contenido}"
    except Exception as e:
        print(f"  ⚠️  Error leyendo {ruta_archivo}: {e}")
        return None


def cargar_diagramas(carpeta: str) -> list[Document]:
    """
    Carga todos los diagramas de una carpeta (Draw.io y Mermaid).

    Args:
        carpeta: Carpeta con los archivos de diagramas.

    Returns:
        Lista de Documentos LangChain.
    """
    documentos = []

    if not os.path.exists(carpeta):
        print(f"  ⚠️  La carpeta {carpeta} no existe.")
        return documentos

    print(f"  🔍 Escaneando diagramas en: {carpeta}")

    for raiz, _, archivos in os.walk(carpeta):
        for archivo in archivos:
            ruta = os.path.join(raiz, archivo)
            extension = Path(archivo).suffix.lower()
            texto = None
            tipo = None

            if extension in [".drawio", ".xml"]:
                texto = parsear_drawio(ruta)
                tipo = "diagrama_drawio"
            elif extension in [".mmd", ".mermaid"]:
                texto = parsear_mermaid(ruta)
                tipo = "diagrama_mermaid"

            if texto:
                doc = Document(
                    page_content=texto,
                    metadata={
                        "fuente": ruta,
                        "tipo": tipo,
                        "nombre_archivo": archivo,
                    }
                )
                documentos.append(doc)

    print(f"  ✅ Diagramas: {len(documentos)} archivos cargados")
    return documentos


# ===== Test =====
if __name__ == "__main__":
    docs = cargar_diagramas("data/diagramas")
    print(f"\nTotal diagramas: {len(docs)}")
    if docs:
        print("\nPrimer diagrama (muestra):")
        print(docs[0].page_content[:500])
