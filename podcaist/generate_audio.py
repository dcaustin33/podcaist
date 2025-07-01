from podcaist.generate_with_eleven_labs import generate_eleven_labs_audio
from podcaist.generate_with_kokoro import generate_kokoro_audio
from podcaist.generate_with_inworld import generate_inworld_audio

podcast_mapping = {
    "eleven_labs": generate_eleven_labs_audio,
    "kokoro": generate_kokoro_audio,
    "inworld": generate_inworld_audio,
}


def generate_audio(
    podcast_title: str, text: str, audio_model: str = "kokoro", remote: bool = False
) -> None:
    """The remote flag is for kokoro on whether to generate the audio locally or on the cloud"""
    return podcast_mapping[audio_model](text=text, remote=remote)
