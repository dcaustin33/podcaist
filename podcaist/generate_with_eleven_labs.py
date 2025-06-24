import os
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    voice: str = "G17SuINrv2H9FC6nvetn",
    model_id: str = "eleven_flash_v2_5",
    output_format: str = "mp3_44100_128",
    remote: bool = True,
    max_workers: int = 4,
) -> str:

    assert remote, "Eleven Labs is not supported locally"
    api_key = os.getenv("ELEVENLABS_API_KEY")
    client = ElevenLabs(api_key=api_key)

    # Split text into chunks if needed
    text_chunks = split_text_at_line_breaks(text)

    # Process each chunk in parallel and combine the audio files
    def generate_chunk_audio(chunk: str) -> str:
        audio = client.text_to_speech.convert(
            text=chunk,
            voice_id=voice,
            model_id=model_id,
            output_format=output_format,
        )
        
        mp3_temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        save(audio, mp3_temp_file.name)
        return mp3_temp_file.name

    temp_files = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chunk = {executor.submit(generate_chunk_audio, chunk): chunk for chunk in text_chunks}
        for future in as_completed(future_to_chunk):
            temp_file = future.result()
            temp_files.append(temp_file)

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


if __name__ == "__main__":
    text = read_text_file(
        "/Users/derek/Desktop/podcaist/podcaist/saved_outputs/Samwise_gemini-2.5-flash_gemini-2.5-flash.txt"
    )
    temp_file = generate_eleven_labs_audio(text)
    local_file_path = "./podcast_outputs/Samwise_gemini-2.5-flash_gemini-2.5-flash_eleven_v3.mp3"
    shutil.copy2(temp_file, local_file_path)