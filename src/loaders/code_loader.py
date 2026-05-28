"""
Loader para Código Fuente.
Soporta:
- Repositorios Git remotos (GitHub/GitLab): los clona automáticamente.
- Carpetas locales con código fuente.

Extensiones soportadas: .py, .js, .ts, .java, .cs, .go, .rb, .php, .cpp, .c, .h,
.html, .css, .sql, .sh, .ps1, .rs, .kt, .swift
"""

import os
import shutil
from pathlib import Path
from git import Repo, GitCommandError
from langchain_core.documents import Document

# Extensiones de código soportadas
EXTENSIONES_CODIGO = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cs", ".go", ".rb",
    ".php", ".cpp", ".c", ".h", ".hpp", ".html", ".css", ".scss",
    ".sql", ".sh", ".ps1", ".rs", ".kt", ".swift", ".vue", ".dart"
}

# Carpetas que ignoramos (no son código relevante)
CARPETAS_IGNORADAS = {
    "node_modules", ".git", "__pycache__", "venv", "env", ".venv",
    "dist", "build", "target", ".idea", ".vscode", "bin", "obj"
}


def clonar_repositorio(url_repo: str, carpeta_destino: str) -> str:
    """
    Clona un repositorio Git en una carpeta local.
    Si la carpeta ya existe, la elimina y vuelve a clonar (para tener la versión más reciente).

    Args:
        url_repo: URL del repositorio (ej: https://github.com/user/repo.git)
        carpeta_destino: Carpeta donde clonar (ej: data/repos/mi-repo)

    Returns:
        Ruta de la carpeta clonada.
    """
    if os.path.exists(carpeta_destino):
        print(f"  ⚠️  La carpeta {carpeta_destino} ya existe. Eliminando...")
        shutil.rmtree(carpeta_destino, ignore_errors=True)

    try:
        print(f"  📥 Clonando {url_repo}...")
        Repo.clone_from(url_repo, carpeta_destino)
        print(f"  ✅ Clonado en {carpeta_destino}")
        return carpeta_destino
    except GitCommandError as e:
        print(f"  ❌ Error al clonar: {e}")
        return None


def cargar_codigo_fuente(carpeta: str, url_repo: str = None) -> list[Document]:
    """
    Carga archivos de código fuente desde una carpeta local o un repositorio Git.

    Args:
        carpeta: Carpeta local con el código (o donde clonar el repo).
        url_repo: (Opcional) URL del repositorio Git. Si se proporciona, lo clona primero.

    Returns:
        Lista de Documentos LangChain con el código y metadatos.
    """
    documentos = []

    # Si se pasó URL, clonar primero
    if url_repo:
        carpeta = clonar_repositorio(url_repo, carpeta)
        if not carpeta:
            return documentos

    if not os.path.exists(carpeta):
        print(f"  ⚠️  La carpeta {carpeta} no existe.")
        return documentos

    print(f"  🔍 Escaneando código en: {carpeta}")
    archivos_procesados = 0

    for raiz, dirs, archivos in os.walk(carpeta):
        # Filtrar carpetas ignoradas
        dirs[:] = [d for d in dirs if d not in CARPETAS_IGNORADAS]

        for archivo in archivos:
            extension = Path(archivo).suffix.lower()

            if extension in EXTENSIONES_CODIGO:
                ruta_completa = os.path.join(raiz, archivo)
                try:
                    with open(ruta_completa, "r", encoding="utf-8", errors="ignore") as f:
                        contenido = f.read()

                    # Saltar archivos vacíos
                    if not contenido.strip():
                        continue

                    documento = Document(
                        page_content=contenido,
                        metadata={
                            "fuente": ruta_completa,
                            "tipo": "codigo",
                            "lenguaje": extension.replace(".", ""),
                            "nombre_archivo": archivo,
                        }
                    )
                    documentos.append(documento)
                    archivos_procesados += 1

                except Exception as e:
                    print(f"  ⚠️  Error al leer {ruta_completa}: {e}")

    print(f"  ✅ Código fuente: {archivos_procesados} archivos cargados")
    return documentos


# ===== Test del módulo =====
if __name__ == "__main__":
    # Ejemplo de uso 1: Carpeta local
    docs = cargar_codigo_fuente("data/repos")
    print(f"\nTotal documentos de código: {len(docs)}")

    # Ejemplo de uso 2: Repositorio remoto (descomentar para probar)
    # docs = cargar_codigo_fuente(
    #     carpeta="data/repos/ejemplo",
    #     url_repo="https://github.com/octocat/Hello-World.git"
    # )
