import os
import tempfile

from faster_whisper import (
    WhisperModel
)
# ─────────────────────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────────────────────
model = WhisperModel(
    "tiny",
    compute_type="int8"
)

# ─────────────────────────────────────────────────────────────
# TRANSCRIBE AUDIO
# ─────────────────────────────────────────────────────────────

def transcribe_audio(audio_bytes):

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as tmp_file:

            tmp_file.write(audio_bytes)

            temp_path = tmp_file.name

        segments, _ = model.transcribe(
            temp_path
        )

        text = ""

        for segment in segments:

            text += segment.text + " "

        return text.strip()

    except Exception:

        return ""

    finally:

        # CLEAN TEMP FILE

        if (
            temp_path
            and os.path.exists(temp_path)
        ):

            os.remove(temp_path)