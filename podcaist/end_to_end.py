import asyncio
import os
import tempfile

from podcaist.generate_audio import generate_audio
from podcaist.generate_podcast_script import (generate_podcast_script,
                                              generate_podcast_script_async)
from podcaist.pdf_utils import compress_pdf


def generate_entire_podcast(
    pdf_path: str,
    model: str = "gemini-2.0-flash-001",
    audio_model: str = "eleven_labs",
    remote: bool = True,
) -> None:
    """
    Generates an entire podcast from a PDF file.

    """

    compressed_pdf_path = pdf_path.replace(".pdf", "_compressed.pdf")
    compress_pdf(pdf_path, compressed_pdf_path)
    podcast_script = asyncio.run(
        generate_podcast_script_async(compressed_pdf_path, model=model)
    )

    podcast_title = os.path.basename(pdf_path).split(".")[0] + "_" + model
    generate_audio(podcast_title, podcast_script, audio_model, remote=remote)

    return None
