import os
import tempfile
from elevenlabs import save
from elevenlabs.client import ElevenLabs


def generate_eleven_labs_audio(
    podcast_title: str,
    text: str,
    voice: str = "JBFqnCBsd6RMkjVDRZzb",
    model_id: str = "eleven_flash_v2_5",
    output_format: str = "mp3_44100_128",
    output_path: str = "./podcast_outputs",
    remote: bool = True,
) -> None:

    assert remote, "Eleven Labs is not supported locally"
    api_key = os.getenv("ELEVENLABS_API_KEY")
    client = ElevenLabs(api_key=api_key)

    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice,
        model_id=model_id,
        output_format=output_format,
    )

    os.makedirs(output_path, exist_ok=True)

    mp3_temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    save(audio, mp3_temp_file.name)
    return mp3_temp_file.name
