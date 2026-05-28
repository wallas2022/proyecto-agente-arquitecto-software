"""
Módulo de Voz (Fase 5.2).
- STT (Speech-to-Text): transcribe audio a texto usando faster-whisper.
- TTS (Text-to-Speech): convierte texto a audio usando gTTS (en español).
"""

import os
import sys
import tempfile
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config

# Variable global para cachear el modelo Whisper (se carga una sola vez)
_modelo_whisper = None


def obtener_modelo_whisper():
    """
    Carga el modelo faster-whisper una sola vez (lazy loading).
    Usa el modelo 'base' que es ligero y suficiente para español.
    """
    global _modelo_whisper
    if _modelo_whisper is None:
        from faster_whisper import WhisperModel
        print("🎙️  Cargando modelo Whisper (base)...")
        # compute_type="int8" lo hace rápido y ligero en CPU
        _modelo_whisper = WhisperModel("base", device="cpu", compute_type="int8")
        print("  ✅ Modelo Whisper listo")
    return _modelo_whisper


def transcribir_audio(datos_audio: bytes) -> str:
    """
    Transcribe audio (bytes) a texto.

    Args:
        datos_audio: Bytes del audio grabado (formato WAV/MP3).

    Returns:
        Texto transcrito en español.
    """
    if not datos_audio:
        return ""

    # Guardar el audio en un archivo temporal
    os.makedirs(config.CARPETA_AUDIO, exist_ok=True)
    ruta_temp = os.path.join(config.CARPETA_AUDIO, f"grabacion_{uuid.uuid4().hex}.wav")

    try:
        with open(ruta_temp, "wb") as f:
            f.write(datos_audio)

        # Transcribir con Whisper
        modelo = obtener_modelo_whisper()
        segmentos, info = modelo.transcribe(ruta_temp, language="es")

        # Unir todos los segmentos
        texto = " ".join(segmento.text for segmento in segmentos).strip()
        return texto

    except Exception as e:
        print(f"  ⚠️  Error transcribiendo audio: {e}")
        return ""
    finally:
        # Limpiar archivo temporal
        if os.path.exists(ruta_temp):
            try:
                os.remove(ruta_temp)
            except Exception:
                pass


def texto_a_voz(texto: str) -> str:
    """
    Convierte texto a un archivo de audio MP3 usando gTTS.

    Args:
        texto: Texto a convertir en voz.

    Returns:
        Ruta del archivo MP3 generado (o None si falla).
    """
    if not texto or not texto.strip():
        return None

    try:
        from gtts import gTTS

        os.makedirs(config.CARPETA_AUDIO, exist_ok=True)
        ruta_mp3 = os.path.join(config.CARPETA_AUDIO, f"respuesta_{uuid.uuid4().hex}.mp3")

        # gTTS puede tener límite de longitud; recortamos textos muy largos
        texto_corto = texto[:2000] if len(texto) > 2000 else texto

        tts = gTTS(text=texto_corto, lang="es", slow=False)
        tts.save(ruta_mp3)

        return ruta_mp3

    except Exception as e:
        print(f"  ⚠️  Error generando voz: {e}")
        return None


# ===== Test del módulo =====
if __name__ == "__main__":
    print("🔊 Probando TTS (texto a voz)...")
    ruta = texto_a_voz("Hola Walter, soy tu arquitecto de software virtual. El sistema de voz funciona correctamente.")
    if ruta:
        print(f"  ✅ Audio generado en: {ruta}")
        print("  Ábrelo para escucharlo.")
    else:
        print("  ❌ No se pudo generar el audio.")