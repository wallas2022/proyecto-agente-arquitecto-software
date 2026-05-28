# 🧠 AI Architect Assistant

Sistema de **Generación Aumentada por Recuperación (RAG)** que actúa como un *Arquitecto de Software Senior virtual*. Centraliza el conocimiento técnico disperso en repositorios de código, diagramas de arquitectura, diccionarios de datos, documentación e infraestructura, permitiendo realizar consultas complejas en lenguaje natural (texto o voz).

---

## ✨ Características

- 📦 **Ingesta multi-formato:** código fuente (Git), diagramas Draw.io/Mermaid, diccionarios de datos (Excel/CSV/JSON), documentación (Markdown/PDF) e infraestructura (Docker/Kubernetes).
- 🔍 **Búsqueda semántica** con embeddings multilingües optimizados para español.
- 🤖 **Respuestas inteligentes** generadas con Llama 3.3 70B vía la API de Groq.
- 🎨 **Interfaz web profesional** tipo chat desarrollada en Streamlit.
- 🎤 **Interacción por voz:** entrada por micrófono (Speech-to-Text) y lectura de respuestas (Text-to-Speech).
- 📚 **Trazabilidad:** muestra las fuentes consultadas y métricas de cada consulta.

---

## 🛠️ Stack Tecnológico

| Categoría | Herramienta |
|---|---|
| Lenguaje | Python 3.11 |
| Orquestador RAG | LangChain |
| Modelo LLM | Llama 3.3 70B (API de Groq) |
| Embeddings | paraphrase-multilingual-MiniLM-L12-v2 |
| Base vectorial | ChromaDB |
| Interfaz | Streamlit |
| Speech-to-Text | faster-whisper |
| Text-to-Speech | gTTS |

---

## 🚀 Instalación

### Requisitos previos
- Python 3.11
- Una clave de API gratuita de [Groq](https://console.groq.com/)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/ai-architect-assistant.git
cd ai-architect-assistant

# 2. Crear y activar el entorno virtual
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1      # Windows
# source venv/bin/activate        # Linux/Mac

# 3. Instalar dependencias
py -m pip install --upgrade pip setuptools wheel
py -m pip install -r requirements.txt
py -m pip install audio-recorder-streamlit

# 4. Configurar la clave de API
# Copia .env.example como .env y coloca tu clave de Groq
```

---

## 📖 Uso

```bash
# 1. Indexar la base de conocimiento (una sola vez)
py src/indexer.py

# 2. Ejecutar la aplicación
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`.

---

## 📂 Estructura del Proyecto

```
.
├── app.py                  # Interfaz Streamlit
├── requirements.txt        # Dependencias
├── .env.example            # Plantilla de configuración
├── data/                   # Base de conocimiento
│   ├── repos/              # Código fuente
│   ├── diagramas/          # Draw.io, Mermaid
│   ├── diccionarios/       # Excel, CSV, JSON
│   ├── documentos/         # Markdown, PDF
│   └── infraestructura/    # Docker, Kubernetes
├── src/
│   ├── config.py           # Configuración central
│   ├── indexer.py          # Indexación
│   ├── rag_engine.py       # Motor RAG
│   ├── voice.py            # Módulo de voz
│   └── loaders/            # Cargadores de archivos
└── assets/                 # Logo y recursos
```

---

## 👥 Autores

Desarrollado por **Walter Rosales** y **Luis Contreras**.

Universidad Mariano Gálvez de Guatemala — Inteligencia Artificial, 2026.

---

## 📄 Licencia

Proyecto académico con fines educativos.
