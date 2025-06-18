import asyncio
import os
import shutil
import tempfile

from podcaist.generate_audio import generate_audio
from podcaist.generate_podcast_script import generate_podcast_script_async
from podcaist.pdf_utils import compress_pdf
from podcaist.progress import Progress


def generate_entire_podcast(
    pdf_path: str,
    model: str = "gemini-2.5-pro-preview-06-05",
    audio_model: str = "eleven_labs",
    remote: bool = False,
    write_output: bool = False,
    save_locally: bool = False,
    local_output_path: str = "./podcast_outputs",
    progress: Progress | None = None,
    test_audio: bool = False,
) -> None:
    if not test_audio:
        compressed_pdf_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=True).name
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
    else:
        podcast_script = "This is a test of the audio system. It should be able to generate audio from a script."

    podcast_title = os.path.basename(pdf_path).split(".")[0] + "_" + model
    temp_file_name = generate_audio(podcast_title, podcast_script, audio_model, remote=remote)

    if save_locally and temp_file_name:
        progress and progress.step("Saving audio locally")
        os.makedirs(local_output_path, exist_ok=True)
        
        file_extension = os.path.splitext(temp_file_name)[1]
        local_file_path = os.path.join(local_output_path, f"{podcast_title}{file_extension}")
        shutil.copy2(temp_file_name, local_file_path)
        
        progress and progress.step(f"Audio saved to {local_file_path}")

    progress and progress.step("Done") 
    return temp_file_name


if __name__ == "__main__":
    pdf_name = "VJEPA.pdf"
    pdf_path = (
        "/Users/derek/Library/Mobile Documents/com~apple~CloudDocs/Desktop/ML Papers 2/papers_to_read/"
        + pdf_name
    )
    generate_entire_podcast(
        pdf_path,
        model="gemini-2.5-pro-preview-06-05",
        audio_model="eleven_labs",
        remote=True,
        save_locally=True,
        test_audio=False,
        write_output=True,
    )