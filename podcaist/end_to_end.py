import asyncio
import os
import tempfile

from podcaist.generate_audio import generate_audio
from podcaist.generate_podcast_script import (
    generate_podcast_script,
    generate_podcast_script_async,
)
from podcaist.pdf_utils import compress_pdf
from podcaist.progress import Progress


def generate_entire_podcast(
    pdf_path: str,
    model: str = "gemini-2.0-flash-001",
    audio_model: str = "kokoro",
    remote: bool = False,
    write_output: bool = False,
    progress: Progress | None = None,
) -> None:

    compressed_pdf_path = pdf_path.replace(".pdf", "_compressed.pdf")
    compress_pdf(pdf_path, compressed_pdf_path)

    progress and progress.step("Generating podcast script")
    podcast_script = asyncio.run(
        generate_podcast_script_async(
            compressed_pdf_path,
            model=model,
            progress=progress,
            write_output=write_output,
        )
    )

    progress and progress.step("Generating audio")
    podcast_title = os.path.basename(pdf_path).split(".")[0] + "_" + model
    temp_file_name = generate_audio(podcast_title, podcast_script, audio_model, remote=remote)

    progress and progress.step("Done") 
    return temp_file_name
