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
    voice: str = "Ronald",
    model_id: str = "inworld-tts-1",
    max_workers: int = 3,
) -> str:
    api_key = os.getenv("INWORLD_API_KEY")

    def generate_chunk_audio(chunk: str) -> bytes:
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
        return response.content

    text_chunks = split_text_at_line_breaks(text)
    temp_files = [None] * len(text_chunks)

    for chunk in text_chunks:
        temp_files[0] = generate_chunk_audio(chunk)
        print(temp_files[0])

    temp_mp3_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    for temp_file in temp_files:
        temp_mp3_file.write(temp_file)
        os.unlink(temp_file)
    temp_mp3_file.flush()

    return temp_mp3_file.name


if __name__ == "__main__":
    text = "Hello I am hoping that this ends up working"
    tmp_file = generate_inworld_audio(text)
    local_file_path = "./podcast_outputs/inworld_test.mp3"
    shutil.copy2(tmp_file, local_file_path)
