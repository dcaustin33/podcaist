import base64
import json
import os
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import requests

from podcaist.utils import read_text_file, split_text_at_line_breaks


def generate_inworld_audio(
    text: str,
    voice: str = "Edward",
    model_id: str = "inworld-tts-1",
    remote: bool = True,
    max_workers: int = 3,
) -> str:

    assert remote, "Inworld is not supported locally"
    api_key = os.getenv("INWORLD_API_KEY")

    # Split text into chunks if needed
    text_chunks = split_text_at_line_breaks(text)

    # Process each chunk in parallel and combine the audio files
    def generate_chunk_audio(chunk: str, chunk_index: int) -> tuple[int, str]:
        url = "https://api.inworld.ai/tts/v1/voice"
        headers = {
            "Authorization": f"Basic {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "text": chunk,
            "voiceId": voice,
            "modelId": model_id,
        }
        response = requests.request("POST", url, json=data, headers=headers)
        response_data = response.json()

        mp3_temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        # Extract audio content from the audioContent field
        audio_bytes = base64.b64decode(response_data["audioContent"])
        mp3_temp_file.write(audio_bytes)
        mp3_temp_file.flush()
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
    tmp_file = generate_inworld_audio(text)
    local_file_path = "./podcast_outputs/inworld_test.mp3"
    shutil.copy2(tmp_file, local_file_path)
