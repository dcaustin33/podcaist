# dia_modal.py
import io

from podcaist.modal_utils import app, image


# 2️⃣  Remote function ------------------------------------------------------------
@app.function(
    gpu="T4",  # pick any GPU on the list in docs (T4, L4, A10G, A100…)  [oai_citation_attribution:0‡Modal](https://modal.com/docs/guide/gpu?utm_source=chatgpt.com)
    timeout=600,  # plenty of time for the first model load
    image=image,
    # If the model is gated add: secrets=[modal.Secret.from_name("huggingface")]
)
def synthesize(text: str, as_mp3: bool = False) -> bytes:
    """
    Turns text → speech with Dia.
    Returns raw bytes (WAV by default, MP3 if as_mp3=True).
    """

    import os
    import subprocess
    import tempfile

    import soundfile as sf
    from dia.model import Dia

    global _dia
    if "_dia" not in globals():
        _dia = Dia.from_pretrained("nari-labs/Dia-1.6B")

    audio = _dia.generate(text)
    buf = io.BytesIO()
    sf.write(buf, audio, 44_100, format="WAV", subtype="PCM_16")
    if not as_mp3:
        return buf.getvalue()

    # Convert to MP3 inside the container with ffmpeg
    buf.seek(0)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_f:
        wav_f.write(buf.read())
        wav_path = wav_f.name

    mp3_path = wav_path.replace(".wav", ".mp3")
    subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-i",
            wav_path,
            "-codec:a",
            "libmp3lame",
            mp3_path,
        ],
        check=True,
    )
    with open(mp3_path, "rb") as mp3_f:
        mp3_bytes = mp3_f.read()

    os.remove(wav_path)
    os.remove(mp3_path)
    return mp3_bytes


# 3️⃣  Local entrypoint -----------------------------------------------------------
@app.local_entrypoint()
def main():
    text = "I am really hoping this works"
    wav = synthesize.remote(text)  # or synthesize.remote(TEXT, as_mp3=True)
    with open("simple.wav", "wb") as f:
        f.write(wav)
    print("Saved simple.wav ✅")


def generate_dia_audio(
    podcast_title: str,
    text: str,
    output_path: str = "./podcast_outputs",
    as_mp3: bool = True,
) -> None:
    with app.run():
        wav = synthesize.remote(text, as_mp3=as_mp3)
        with open(f"{output_path}/{podcast_title}.mp3", "wb") as f:
            f.write(wav)
