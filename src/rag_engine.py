"""
Motor RAG (Fase 4).
Conecta:
- El retriever de ChromaDB (búsqueda semántica).
- El LLM de Groq (generación de respuestas).
- Un prompt especializado de "Arquitecto de Software Senior".
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

import config
from indexer import cargar_base_vectorial_existente


# ===== PROMPT DEL ARQUITECTO SENIOR =====
PLANTILLA_PROMPT = """Eres un Arquitecto de Software Senior virtual con amplia experiencia. \
Tu trabajo es responder preguntas técnicas sobre el sistema usando ÚNICAMENTE la información \
del CONTEXTO proporcionado (código fuente, diagramas de arquitectura, diccionarios de datos, \
documentación e infraestructura).

INSTRUCCIONES:
1. Responde de forma clara, técnica y profesional, como lo haría un arquitecto senior.
2. Cuando menciones código, archivos o componentes, cita la fuente (nombre del archivo).
3. Si la pregunta es sobre IMPACTO de cambios, analiza qué componentes podrían verse afectados.
4. Si la pregunta es sobre LINAJE de datos, explica de dónde viene y hacia dónde fluye la información.
5. Si la información NO está en el contexto, dilo claramente: "No encuentro esa información en la \
base de conocimiento actual." NO inventes datos.
6. Responde siempre en español.

CONTEXTO:
{contexto}

PREGUNTA DEL USUARIO:
{pregunta}

RESPUESTA DEL ARQUITECTO SENIOR:"""


def formatear_documentos(docs) -> str:
    """
    Convierte los documentos recuperados en un texto de contexto,
    incluyendo la fuente de cada fragmento.
    """
    partes = []
    for i, doc in enumerate(docs, start=1):
        fuente = doc.metadata.get("nombre_archivo", doc.metadata.get("fuente", "desconocida"))
        tipo = doc.metadata.get("tipo", "desconocido")
        partes.append(
            f"[Fragmento {i} | Fuente: {fuente} | Tipo: {tipo}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(partes)


class MotorRAG:
    """
    Clase principal que encapsula todo el sistema RAG.
    """

    def __init__(self):
        print("🧠 Inicializando Motor RAG...")

        # Validar API Key
        if not config.GROQ_API_KEY:
            raise ValueError(
                "❌ No se encontró GROQ_API_KEY. "
                "Verifica que el archivo .env tenga tu clave de Groq."
            )

        # Cargar la base vectorial
        self.vectorstore = cargar_base_vectorial_existente()
        if self.vectorstore is None:
            raise ValueError(
                "❌ No existe la base vectorial. Ejecuta primero: py src/indexer.py"
            )

        # Crear el retriever
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": config.NUM_RESULTADOS}
        )

        # Crear el LLM de Groq
        self.llm = ChatGroq(
            groq_api_key=config.GROQ_API_KEY,
            model_name=config.MODELO_LLM,
            temperature=config.TEMPERATURA,
        )

        # Crear el prompt
        self.prompt = ChatPromptTemplate.from_template(PLANTILLA_PROMPT)

        # Parser de salida
        self.parser = StrOutputParser()

        print("  ✅ Motor RAG listo")

    def consultar(self, pregunta: str) -> dict:
        """
        Procesa una consulta completa:
        1. Recupera fragmentos relevantes.
        2. Genera respuesta con el LLM.
        3. Devuelve respuesta + fuentes + métricas.

        Returns:
            dict con: respuesta, fuentes, tiempo, num_fragmentos
        """
        inicio = time.time()

        # 1. Recuperar documentos relevantes
        docs_relevantes = self.retriever.invoke(pregunta)

        # 2. Formatear el contexto
        contexto = formatear_documentos(docs_relevantes)

        # 3. Construir la cadena y generar respuesta
        cadena = self.prompt | self.llm | self.parser
        respuesta = cadena.invoke({
            "contexto": contexto,
            "pregunta": pregunta
        })

        tiempo_total = time.time() - inicio

        # 4. Preparar información de las fuentes
        fuentes = []
        for doc in docs_relevantes:
            fuentes.append({
                "nombre": doc.metadata.get("nombre_archivo", "desconocido"),
                "tipo": doc.metadata.get("tipo", "desconocido"),
                "fuente": doc.metadata.get("fuente", ""),
                "extracto": doc.page_content[:200],
            })

        return {
            "respuesta": respuesta,
            "fuentes": fuentes,
            "tiempo": round(tiempo_total, 2),
            "num_fragmentos": len(docs_relevantes),
        }


# ===== Test del motor en consola =====
if __name__ == "__main__":
    print("=" * 70)
    print("ARQUITECTO SENIOR RAG - Motor RAG (Fase 4)")
    print("=" * 70)

    try:
        motor = MotorRAG()
    except ValueError as e:
        print(e)
        sys.exit(1)

    print("\n Motor listo. Hazme preguntas sobre tu sistema.")
    print("   (Escribe 'salir' para terminar)\n")

    while True:
        pregunta = input(" Tu pregunta: ").strip()

        if pregunta.lower() in ["salir", "exit", "quit", ""]:
            print("\n ¡Hasta luego!")
            break

        print("\n⏳ Pensando...\n")
        resultado = motor.consultar(pregunta)

        print("=" * 70)
        print("RESPUESTA DEL ARQUITECTO SENIOR:")
        print("=" * 70)
        print(resultado["respuesta"])
        print("\n" + "-" * 70)
        print(f"Fragmentos usados: {resultado['num_fragmentos']} | "
              f"Tiempo: {resultado['tiempo']}s")
        print("Fuentes consultadas:")
        for f in resultado["fuentes"]:
            print(f"   • {f['nombre']} ({f['tipo']})")
        print("=" * 70 + "\n")