"""
Loader para Archivos de Infraestructura.
Soporta:
- Dockerfile
- docker-compose.yaml / .yml
- Manifiestos de Kubernetes (.yaml / .yml)
"""

import os
from pathlib import Path
from langchain_core.documents import Document


# Nombres y extensiones que indican infraestructura
NOMBRES_INFRA = {"dockerfile", "docker-compose.yaml", "docker-compose.yml"}
EXTENSIONES_INFRA = {".yaml", ".yml"}


def detectar_tipo_infra(ruta_archivo: str, contenido: str) -> str:
    """
    Detecta qué tipo de archivo de infraestructura es.
    """
    nombre = os.path.basename(ruta_archivo).lower()

    if nombre == "dockerfile":
        return "dockerfile"
    elif "docker-compose" in nombre:
        return "docker-compose"
    elif any(kw in contenido for kw in ["apiVersion:", "kind: Deployment", "kind: Service", "kind: Pod", "kind: ConfigMap"]):
        return "kubernetes"
    else:
        return "yaml_generico"


def leer_archivo_infra(ruta_archivo: str) -> Document:
    """
    Lee un archivo de infraestructura y lo procesa.
    """
    try:
        with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
            contenido = f.read()

        if not contenido.strip():
            return None

        tipo_infra = detectar_tipo_infra(ruta_archivo, contenido)

        # Encabezado descriptivo según el tipo
        encabezados = {
            "dockerfile": "ARCHIVO DOCKERFILE",
            "docker-compose": "ARCHIVO DOCKER-COMPOSE",
            "kubernetes": "MANIFIESTO DE KUBERNETES",
            "yaml_generico": "ARCHIVO YAML",
        }

        texto = f"{encabezados[tipo_infra]}: {os.path.basename(ruta_archivo)}\n\n"
        texto += contenido

        return Document(
            page_content=texto,
            metadata={
                "fuente": ruta_archivo,
                "tipo": f"infraestructura_{tipo_infra}",
                "nombre_archivo": os.path.basename(ruta_archivo),
            }
        )
    except Exception as e:
        print(f"  ⚠️  Error leyendo {ruta_archivo}: {e}")
        return None


def cargar_infraestructura(carpeta: str) -> list[Document]:
    """
    Carga todos los archivos de infraestructura de una carpeta.
    """
    documentos = []

    if not os.path.exists(carpeta):
        print(f"  ⚠️  La carpeta {carpeta} no existe.")
        return documentos

    print(f"  🔍 Escaneando infraestructura en: {carpeta}")

    for raiz, _, archivos in os.walk(carpeta):
        for archivo in archivos:
            ruta = os.path.join(raiz, archivo)
            nombre_lower = archivo.lower()
            extension = Path(archivo).suffix.lower()

            # Es archivo de infraestructura si:
            # 1. Su nombre es Dockerfile o docker-compose
            # 2. O tiene extensión .yaml/.yml
            if nombre_lower in NOMBRES_INFRA or extension in EXTENSIONES_INFRA:
                doc = leer_archivo_infra(ruta)
                if doc:
                    documentos.append(doc)

    print(f"  ✅ Infraestructura: {len(documentos)} archivos cargados")
    return documentos


# ===== Test =====
if __name__ == "__main__":
    docs = cargar_infraestructura("data/infraestructura")
    print(f"\nTotal archivos infraestructura: {len(docs)}")
    if docs:
        print("\nPrimer archivo (muestra):")
        print(docs[0].page_content[:500])
