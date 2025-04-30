import os
from elevenlabs import save
from elevenlabs.client import ElevenLabs

from podcaist.api_secrets import elevenlabs_api_key


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
    client = ElevenLabs(api_key=elevenlabs_api_key)

    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice,
        model_id=model_id,
        output_format=output_format,
    )

    os.makedirs(output_path, exist_ok=True)
    save(audio, f"{output_path}/{podcast_title}_eleven_labs.mp3")
    return None
