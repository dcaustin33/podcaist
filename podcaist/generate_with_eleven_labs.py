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
    voice: str = "nPczCjzI2devNBz1zQrb",
    model_id: str = "eleven_multilingual_v2",
    output_format: str = "mp3_44100_128",
    remote: bool = True,
    max_workers: int = 3,
) -> str:

    assert remote, "Eleven Labs is not supported locally"
    api_key = os.getenv("ELEVENLABS_API_KEY")
    client = ElevenLabs(api_key=api_key)

    # Split text into chunks if needed
    text_chunks = split_text_at_line_breaks(text)

    # Process each chunk in parallel and combine the audio files
    def generate_chunk_audio(chunk: str, chunk_index: int) -> tuple[int, str]:
        audio = client.text_to_speech.convert(
            text=chunk,
            voice_id=voice,
            model_id=model_id,
            output_format=output_format,
        )

        mp3_temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        save(audio, mp3_temp_file.name)
        return chunk_index, mp3_temp_file.name

    temp_files = [None] * len(text_chunks)  # Pre-allocate list to maintain order
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chunk = {
            executor.submit(generate_chunk_audio, chunk, i): chunk
            for i, chunk in enumerate(text_chunks)
        }
        for future in as_completed(future_to_chunk):
            chunk_index, temp_file = future.result()
            temp_files[chunk_index] = temp_file

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
        "/Users/derek/Desktop/podcaist/podcaist/saved_outputs/Reinforcement Learning Teachers of Test Time Scaling_gemini-2.5-pro_gemini-2.5-pro.txt"
    )
    temp_file = generate_eleven_labs_audio(text)
    local_file_path = "./podcast_outputs/Reinforcement Learning Teachers of Test Time Scaling_gemini-2.5-pro_gemini-2.5-pro-full.mp3"
    shutil.copy2(temp_file, local_file_path)
