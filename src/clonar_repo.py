"""
Helper para clonar repositorios Git remotos a la base de conocimiento.

USO:
    py src\clonar_repo.py <URL_DEL_REPO> [nombre_carpeta_opcional]

EJEMPLOS:
    py src\clonar_repo.py https://github.com/wallas2022/proyecto-agente-arquitecto-software.git
    py src\clonar_repo.py https://github.com/usuario/mi-proyecto.git mi-proyecto
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from loaders.code_loader import clonar_repositorio


def main():
    if len(sys.argv) < 2:
        print("❌ Falta la URL del repositorio.")
        print("\nUSO:")
        print("    py src\\clonar_repo.py <URL_DEL_REPO> [nombre_carpeta_opcional]")
        print("\nEJEMPLOS:")
        print("    py src\\clonar_repo.py https://github.com/usuario/repo.git")
        print("    py src\\clonar_repo.py https://github.com/usuario/repo.git mi-repo")
        return

    url_repo = sys.argv[1]

    # Determinar el nombre de la carpeta
    if len(sys.argv) >= 3:
        nombre_carpeta = sys.argv[2]
    else:
        # Extraer el nombre del repo desde la URL
        nombre_carpeta = url_repo.rstrip("/").split("/")[-1].replace(".git", "")

    carpeta_destino = os.path.join(config.CARPETA_REPOS, nombre_carpeta)

    print("=" * 70)
    print("📥 CLONADOR DE REPOSITORIOS GIT")
    print("=" * 70)
    print(f"  URL:     {url_repo}")
    print(f"  Destino: {carpeta_destino}")
    print("=" * 70)

    resultado = clonar_repositorio(url_repo, carpeta_destino)

    if resultado:
        print("\n✅ Repositorio clonado exitosamente.")
        print(f"\n📌 Próximo paso: ejecuta la indexación para incluirlo en la base:")
        print(f"    py src\\indexer.py")
    else:
        print("\n❌ No se pudo clonar el repositorio.")
        print("   Verifica que la URL sea correcta y que tengas conexión a internet.")
        print("   Si es un repo privado, necesitas autenticación.")


if __name__ == "__main__":
    main()