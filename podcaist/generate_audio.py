from podcaist.generate_with_dia import app, generate_dia_audio
from podcaist.generate_with_eleven_labs import generate_eleven_labs_audio
from podcaist.generate_with_kokoro import generate_kokoro_audio

podcast_mapping = {
    "eleven_labs": generate_eleven_labs_audio,
    "kokoro": generate_kokoro_audio,
    "dia": generate_dia_audio,
}


def generate_audio(
    podcast_title: str, text: str, audio_model: str = "kokoro", remote: bool = False
) -> None:
    podcast_mapping[audio_model](podcast_title, text, remote=remote)
