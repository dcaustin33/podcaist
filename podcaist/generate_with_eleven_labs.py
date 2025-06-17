import os
import tempfile

from elevenlabs import save
from elevenlabs.client import ElevenLabs

from podcaist.utils import read_text_file


def generate_eleven_labs_audio(
    podcast_title: str,
    text: str,
    voice: str = "bIHbv24MWmeRgasZH58o",
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


if __name__ == "__main__":
    podcast_title = "Swin Transformer"
    text = read_text_file(
        "/Users/derek/Desktop/podcaist/podcaist/blind_test_results3/test_001.txt"
    )
    temp_file = generate_eleven_labs_audio(podcast_title, text)

    # Create a filename from the podcast title
    safe_title = "".join(c if c.isalnum() else "_" for c in podcast_title.lower())
    output_path = "./podcast_outputs"
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, f"{safe_title}.mp3")

    # Move the temp file to the final location
    os.rename(temp_file, output_file)
    print(f"Audio saved to: {output_file}")
