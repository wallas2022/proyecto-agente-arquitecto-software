"""
AI Architect Assistant - Interfaz Streamlit (Fase 5 + Voz) - VERSIÓN FINAL
Logo UMG junto al título (izquierda) y créditos de autores.
Conectado al Motor RAG (Groq + ChromaDB).

Ejecutar desde la raíz del proyecto:
    streamlit run app.py
"""

import sys
import os
import re
import html
import base64

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

import streamlit as st
from rag_engine import MotorRAG
from voice import transcribir_audio, texto_a_voz

try:
    from audio_recorder_streamlit import audio_recorder
    VOZ_DISPONIBLE = True
except ImportError:
    VOZ_DISPONIBLE = False

st.set_page_config(
    page_title="AI Architect Assistant - UMG",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .stApp > header { background-color: transparent; }
    div[data-testid="stVerticalBlock"] > div:empty { display: none; }

    .header-box {
        background: linear-gradient(135deg, #1c2638 0%, #161b22 100%);
        padding: 22px 26px; border-radius: 14px; border: 1px solid #2d3748;
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    /* Encabezado con logo a la izquierda */
    .header-flex {
        display: flex; align-items: center; gap: 18px;
    }
    .header-flex img { height: 64px; width: auto; flex-shrink: 0; }
    .header-title { font-size: 28px; font-weight: 800; color: #ffffff; margin: 0; }
    .header-subtitle { font-size: 14px; color: #94a3b8; margin: 5px 0 0 0; }

    .panel-box {
        background-color: #161b22; padding: 18px; border-radius: 12px;
        border: 1px solid #2d3748; margin-bottom: 15px;
    }
    .panel-title {
        font-size: 12px; font-weight: 700; color: #7dd3fc;
        text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 14px;
    }

    .fuente-card {
        background-color: #1e2530; padding: 13px; border-radius: 8px;
        border: 1px solid #2d3748; border-left: 3px solid #38bdf8; margin-bottom: 10px;
    }
    .fuente-nombre { font-size: 13px !important; font-weight: 700; color: #38bdf8; word-break: break-word; }
    .fuente-tipo {
        font-size: 10px !important; color: #94a3b8; background-color: #0d1117;
        padding: 2px 8px; border-radius: 10px;
    }
    .fuente-extracto {
        font-size: 11px !important; color: #cbd5e1 !important; margin-top: 8px !important;
        font-family: 'Consolas', monospace; line-height: 1.5 !important; font-weight: 400 !important;
        white-space: pre-wrap; word-break: break-word;
    }

    .stat-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 0; border-bottom: 1px solid #21262d;
    }
    .stat-label { color: #cbd5e1; font-size: 14px; }
    .stat-value { color: #38bdf8; font-weight: 700; font-size: 16px; }

    .badge-conectado {
        display: inline-block; background-color: #14532d; color: #4ade80;
        padding: 6px 14px; border-radius: 20px; font-size: 13px; font-weight: 700;
        border: 1px solid #22c55e;
    }

    .stChatInput textarea, .stChatInput input {
        background-color: #1e2530 !important; color: #e6edf3 !important;
        border: 1px solid #38bdf8 !important; border-radius: 10px !important;
    }
    .stChatInput textarea::placeholder { color: #94a3b8 !important; }
    div[data-testid="stChatInput"] {
        background-color: #1e2530 !important; border-radius: 10px !important; border: 1px solid #2d3748 !important;
    }

    .stButton button {
        background-color: #1e2530 !important; color: #e6edf3 !important;
        border: 1px solid #38bdf8 !important; border-radius: 10px !important;
        font-size: 13px !important; font-weight: 500 !important; text-align: left !important;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        background-color: #2563eb !important; color: #ffffff !important; border-color: #2563eb !important;
    }

    div[data-testid="stChatMessage"] {
        background-color: #161b22; border-radius: 12px; border: 1px solid #2d3748;
        padding: 12px; margin-bottom: 8px;
    }
    div[data-testid="stChatMessage"] p,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] span,
    div[data-testid="stChatMessage"] div {
        color: #e6edf3 !important; font-size: 15px !important; line-height: 1.65 !important;
    }
    div[data-testid="stChatMessage"] strong { color: #ffffff !important; }
    div[data-testid="stChatMessage"] h1,
    div[data-testid="stChatMessage"] h2,
    div[data-testid="stChatMessage"] h3 { color: #7dd3fc !important; font-size: 18px !important; }
    div[data-testid="stChatMessage"] code {
        color: #7ee787 !important; background-color: #0d1117 !important;
        padding: 2px 6px; border-radius: 4px;
    }

    .footer-creditos {
        text-align: center; color: #94a3b8; font-size: 13px; margin-top: 30px;
        padding: 16px; border-top: 1px solid #2d3748;
    }
    .footer-creditos strong { color: #7dd3fc; }
</style>
""", unsafe_allow_html=True)


def cargar_logo_base64(ruta):
    try:
        with open(ruta, "rb") as f:
            datos = f.read()
        return base64.b64encode(datos).decode()
    except Exception:
        return None


def limpiar_extracto(texto, max_chars=180):
    if not texto:
        return ""
    texto = re.sub(r'^#{1,6}\s*', '', texto, flags=re.MULTILINE)
    texto = texto.replace('**', '').replace('__', '').replace('*', '').replace('`', '')
    texto = re.sub(r'\n{2,}', ' ', texto)
    texto = texto.replace('\n', ' ')
    texto = re.sub(r'\s{2,}', ' ', texto).strip()
    texto = html.escape(texto)
    if len(texto) > max_chars:
        texto = texto[:max_chars] + "..."
    return texto


@st.cache_resource
def inicializar_motor():
    return MotorRAG()


if "mensajes" not in st.session_state:
    st.session_state.mensajes = []
if "ultimas_fuentes" not in st.session_state:
    st.session_state.ultimas_fuentes = []
if "ultimo_tiempo" not in st.session_state:
    st.session_state.ultimo_tiempo = 0
if "consultas_hoy" not in st.session_state:
    st.session_state.consultas_hoy = 0
if "audio_respuesta" not in st.session_state:
    st.session_state.audio_respuesta = None
if "ultimo_audio_hash" not in st.session_state:
    st.session_state.ultimo_audio_hash = None


try:
    motor = inicializar_motor()
    motor_ok = True
except Exception as e:
    motor_ok = False
    error_motor = str(e)


# ===== Cargar logo UMG =====
RUTA_LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "logo_umg.png")
logo_b64 = cargar_logo_base64(RUTA_LOGO)
logo_html = f'<img src="data:image/png;base64,{logo_b64}" alt="Logo UMG">' if logo_b64 else ""


# ===== ENCABEZADO (logo a la izquierda junto al título) =====
col_titulo, col_estado = st.columns([3, 1])
with col_titulo:
    st.markdown(f"""
    <div class="header-box">
        <div class="header-flex">
            {logo_html}
            <div>
                <p class="header-title">🧠 AI Architect Assistant</p>
                <p class="header-subtitle">Tu arquitecto de software inteligente</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col_estado:
    estado = '<span class="badge-conectado">● Conectado a ChromaDB</span>' if motor_ok \
        else '<span style="color:#f85149; font-weight:700;">● Sin conexión</span>'
    st.markdown(f"""
    <div class="header-box" style="text-align:center;">
        {estado}
        <p class="header-subtitle" style="margin-top:10px;">Modelo: Llama 3.3 70B</p>
    </div>
    """, unsafe_allow_html=True)


if not motor_ok:
    st.error(f"❌ No se pudo iniciar el motor RAG:\n\n{error_motor}")
    st.info("Verifica que: 1) Ejecutaste py src/indexer.py, 2) Tu archivo .env tiene GROQ_API_KEY")
    st.stop()


def procesar_pregunta(pregunta_texto, leer_voz=False):
    st.session_state.mensajes.append({"rol": "user", "contenido": pregunta_texto})
    resultado = motor.consultar(pregunta_texto)
    st.session_state.mensajes.append({"rol": "assistant", "contenido": resultado["respuesta"]})
    st.session_state.ultimas_fuentes = resultado["fuentes"]
    st.session_state.ultimo_tiempo = resultado["tiempo"]
    st.session_state.consultas_hoy += 1
    if leer_voz:
        st.session_state.audio_respuesta = texto_a_voz(resultado["respuesta"])
    else:
        st.session_state.audio_respuesta = None


col_nav, col_chat, col_fuentes = st.columns([1, 2.5, 1.3])


with col_nav:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown('<p class="panel-title">📊 Estadísticas</p>', unsafe_allow_html=True)
    num_docs = len(st.session_state.ultimas_fuentes)
    st.markdown(f"""
        <div class="stat-row">
            <span class="stat-label">💬 Consultas hoy</span>
            <span class="stat-value">{st.session_state.consultas_hoy}</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">⏱️ Último tiempo</span>
            <span class="stat-value">{st.session_state.ultimo_tiempo}s</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">📄 Fuentes últimas</span>
            <span class="stat-value">{num_docs}</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="panel-box">
        <p class="panel-title">👤 Desarrolladores</p>
        <p style="color:#ffffff; font-weight:700; margin:0; font-size:15px;">Walter Rosales</p>
        <p style="color:#ffffff; font-weight:700; margin:6px 0 0 0; font-size:15px;">Luis Contreras</p>
        <p style="color:#94a3b8; font-size:12px; margin:6px 0 0 0;">Arquitectos de Software</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="panel-title" style="margin-top:10px;">🎤 Pregunta por voz</p>',
                unsafe_allow_html=True)
    if VOZ_DISPONIBLE:
        audio_bytes = audio_recorder(
            text="Haz clic para grabar",
            recording_color="#e74c3c",
            neutral_color="#38bdf8",
            icon_size="2x",
        )
        if audio_bytes:
            audio_hash = hash(audio_bytes)
            if audio_hash != st.session_state.ultimo_audio_hash:
                st.session_state.ultimo_audio_hash = audio_hash
                with st.spinner("🎙️ Transcribiendo tu voz..."):
                    texto_voz = transcribir_audio(audio_bytes)
                if texto_voz:
                    st.success(f"🗣️ Entendí: {texto_voz}")
                    procesar_pregunta(texto_voz, leer_voz=True)
                    st.rerun()
                else:
                    st.warning("No pude entender el audio. Intenta de nuevo.")
    else:
        st.info("Instala: pip install audio-recorder-streamlit para activar la voz.")

    st.markdown('<p class="panel-title" style="margin-top:10px;">💡 Preguntas sugeridas</p>',
                unsafe_allow_html=True)
    sugerencias = [
        "¿Qué fases tiene el cronograma?",
        "¿Qué componentes tiene la arquitectura?",
        "¿Qué tablas maneja el sistema?",
    ]
    for sug in sugerencias:
        if st.button(sug, key=f"sug_{sug}", use_container_width=True):
            st.session_state.pregunta_sugerida = sug


with col_chat:
    st.markdown("""
    <div class="panel-box">
        <p style="font-size:24px; font-weight:800; color:#fff; margin:0;">¡Hola! 👋</p>
        <p style="color:#94a3b8; margin:8px 0 0 0; font-size:15px;">Soy tu Arquitecto de Software IA.
        Pregúntame por texto o por voz sobre tu arquitectura, código, servicios o cualquier aspecto técnico.</p>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.mensajes:
        with st.chat_message(msg["rol"], avatar="🧑" if msg["rol"] == "user" else "🧠"):
            st.markdown(msg["contenido"])

    if st.session_state.audio_respuesta and os.path.exists(st.session_state.audio_respuesta):
        st.markdown('<p style="color:#7dd3fc; font-size:13px; margin-top:10px;">🔊 Escuchar respuesta:</p>',
                    unsafe_allow_html=True)
        st.audio(st.session_state.audio_respuesta, format="audio/mp3")

    pregunta = st.chat_input("Escribe tu pregunta aquí...")

    if "pregunta_sugerida" in st.session_state:
        pregunta = st.session_state.pregunta_sugerida
        del st.session_state.pregunta_sugerida

    if pregunta:
        with st.spinner("🧠 Analizando tu base de conocimiento..."):
            procesar_pregunta(pregunta, leer_voz=False)
        st.rerun()


with col_fuentes:
    st.markdown('<div class="panel-box">', unsafe_allow_html=True)
    st.markdown('<p class="panel-title">📚 Fuentes utilizadas</p>', unsafe_allow_html=True)
    if st.session_state.ultimas_fuentes:
        for f in st.session_state.ultimas_fuentes:
            extracto_limpio = limpiar_extracto(f['extracto'])
            st.markdown(f"""
            <div class="fuente-card">
                <span class="fuente-nombre">{html.escape(f['nombre'])}</span><br>
                <span class="fuente-tipo">{html.escape(f['tipo'])}</span>
                <p class="fuente-extracto">{extracto_limpio}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<p style="color:#94a3b8; font-size:13px;">Haz una consulta para ver las fuentes utilizadas.</p>',
                    unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.ultimas_fuentes:
        st.markdown(f"""
        <div class="panel-box">
            <p class="panel-title">🔍 Detalles de la consulta</p>
            <div class="stat-row">
                <span class="stat-label">Modelo</span>
                <span class="stat-value" style="font-size:13px;">Llama 3.3 70B</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Tiempo</span>
                <span class="stat-value">{st.session_state.ultimo_tiempo}s</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Fragmentos</span>
                <span class="stat-value">{len(st.session_state.ultimas_fuentes)}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)


st.markdown("""
<div class="footer-creditos">
    Desarrollado por <strong>Walter Rosales</strong> y <strong>Luis Contreras</strong><br>
    Universidad Mariano Gálvez de Guatemala &nbsp;|&nbsp; Inteligencia Artificial 2026<br>
    <span style="font-size:11px; color:#64748b;">AI Architect Assistant v1.0.0 · Arquitectura RAG con ChromaDB + Groq + Voz</span>
</div>
""", unsafe_allow_html=True)
