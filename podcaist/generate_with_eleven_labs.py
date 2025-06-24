import os
import tempfile
from typing import List

from elevenlabs import save
from elevenlabs.client import ElevenLabs

from podcaist.utils import read_text_file


def split_text_at_line_breaks(text: str, max_length: int = 3000) -> List[str]:
    """Split text into chunks at line breaks, ensuring no chunk exceeds max_length."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""

    for line in text.split("\n"):
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + "\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + "\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def generate_eleven_labs_audio(
    text: str,
    voice: str = "nPczCjzI2devNBz1zQrb",
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
    remote: bool = True,
) -> str:

    assert remote, "Eleven Labs is not supported locally"
    api_key = os.getenv("ELEVENLABS_API_KEY")
    client = ElevenLabs(api_key=api_key)

    # Split text into chunks if needed
    text_chunks = split_text_at_line_breaks(text)

    # Process each chunk and combine the audio files
    temp_files = []
    # TODO: parallelize this
    for chunk in text_chunks:
        audio = client.text_to_speech.convert(
            text=chunk,
            voice_id=voice,
            model_id=model_id,
            output_format=output_format,
        )

        mp3_temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        save(audio, mp3_temp_file.name)
        temp_files.append(mp3_temp_file.name)

    # If we only have one chunk, return it directly
    if len(temp_files) == 1:
        return temp_files[0]

    # Combine multiple audio files
    from pydub import AudioSegment

    combined = AudioSegment.from_mp3(temp_files[0])
    for temp_file in temp_files[1:]:
        combined += AudioSegment.from_mp3(temp_file)

    # Save the combined audio
    final_temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    combined.export(final_temp_file.name, format="mp3")

    # Clean up intermediate files
    for temp_file in temp_files:
        os.unlink(temp_file)

    return final_temp_file.name
