"""
Configuración central del Arquitecto Senior RAG.
Aquí se centralizan todos los ajustes del sistema.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# ===== RUTAS DEL PROYECTO =====
# Carpeta raíz del proyecto (un nivel arriba de src/)
RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Carpetas de datos
CARPETA_DATA = os.path.join(RAIZ_PROYECTO, "data")
CARPETA_REPOS = os.path.join(CARPETA_DATA, "repos")
CARPETA_DIAGRAMAS = os.path.join(CARPETA_DATA, "diagramas")
CARPETA_DICCIONARIOS = os.path.join(CARPETA_DATA, "diccionarios")
CARPETA_DOCUMENTOS = os.path.join(CARPETA_DATA, "documentos")
CARPETA_INFRAESTRUCTURA = os.path.join(CARPETA_DATA, "infraestructura")

# Carpeta de la base vectorial
CARPETA_VECTORSTORE = os.path.join(RAIZ_PROYECTO, "vectorstore")

# Carpeta de audio (para voz)
CARPETA_AUDIO = os.path.join(RAIZ_PROYECTO, "audio")

# ===== CONFIGURACIÓN DE CHUNKING =====
# Tamaño de cada fragmento (en caracteres)
CHUNK_SIZE = 1000
# Superposición entre fragmentos (para no perder contexto en los bordes)
CHUNK_OVERLAP = 150

# ===== CONFIGURACIÓN DE EMBEDDINGS =====
# Modelo de embeddings multilingüe (funciona muy bien en español)
# Es gratuito y se descarga automáticamente la primera vez (~470 MB)
MODELO_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# ===== CONFIGURACIÓN DE CHROMADB =====
NOMBRE_COLECCION = "arquitecto_senior"

# ===== CONFIGURACIÓN DEL LLM (GROQ) =====
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Modelo de Groq a usar (Llama 3.3 70B es muy bueno y rápido)
MODELO_LLM = "llama-3.3-70b-versatile"
# Temperatura: 0 = más preciso/determinista, 1 = más creativo
TEMPERATURA = 0.2

# ===== CONFIGURACIÓN DEL RETRIEVER =====
# Cuántos fragmentos relevantes recuperar por consulta
NUM_RESULTADOS = 5
