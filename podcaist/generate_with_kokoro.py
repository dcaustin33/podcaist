import os
import tempfile

import numpy as np
import pydub
import soundfile as sf
from kokoro import KPipeline

from podcaist.modal_utils import app, image


# 2️⃣  Remote function ------------------------------------------------------------
@app.function(
    gpu="T4", 
    timeout=600,  # plenty of time for the first model load
    image=image,
    # If the model is gated add: secrets=[modal.Secret.from_name("huggingface")]
)
def generate_kokoro_modal(text: str, voice: str = "kokoro") -> bytes:
    """
    Turns text → speech with Kokoro.
    Returns raw bytes (WAV by default, MP3 if as_mp3=True).
    """

    from kokoro import KPipeline

    global _kokoro_pipeline
    if "_kokoro_pipeline" not in globals():
        _kokoro_pipeline = KPipeline(lang_code="a")

    generator = _kokoro_pipeline(text, voice=voice)

    audio_segments = []
    for i, (gs, ps, audio) in enumerate(generator):
        audio_segments.append(audio.numpy())

    return audio_segments


def generate_kokoro_audio_local(
    text: str,
    voice: str = "af_heart",
) -> None:
    from kokoro import KPipeline

    pipeline = KPipeline(lang_code="a")
    generator = pipeline(text, voice=voice)

    audio_segments = []
    for i, (gs, ps, audio) in enumerate(generator):
        audio_segments.append(audio.numpy())

    return audio_segments


def generate_kokoro_audio(
    text: str,
    voice: str = "af_heart",
    remote: bool = False,
) -> None:
    if remote:
        with app.run():
            audio_segments = generate_kokoro_modal.remote(text, voice=voice)
    else:
        audio_segments = generate_kokoro_audio_local(text, voice=voice)

    if audio_segments:
        combined_audio = np.concatenate(audio_segments, axis=0)
        wav_temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=True)
        sf.write(wav_temp_file.name, combined_audio, 24000)
        wav_temp_file.flush()

        mp3_temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        pydub.AudioSegment.from_wav(wav_temp_file.name).export(
            mp3_temp_file.name, format="mp3"
        )

        return mp3_temp_file.name

    return None
