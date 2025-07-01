import asyncio
import os
import shutil
import tempfile

from podcaist.generate_audio import generate_audio
from podcaist.generate_podcast_script import generate_podcast_script_async
from podcaist.pdf_utils import compress_pdf
from podcaist.progress import Progress
from podcaist.utils import write_text_file


def generate_entire_podcast(
    pdf_path: str,
    model: str = "gemini-2.5-pro",
    audio_model: str = "eleven_labs",
    remote: bool = False,
    save_script_locally: bool = False,
    save_audio_locally: bool = False,
    local_output_path: str = "./podcast_outputs",
    progress: Progress | None = None,
    test_audio: bool = False,
    custom_instructions: str | None = None,
    api_key: str | None = None,
) -> None:
    podcast_title = os.path.basename(pdf_path).split(".")[0] + "_" + model
    if not test_audio:
        compressed_pdf_path = tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=True
        ).name
        compress_pdf(pdf_path, compressed_pdf_path)

        progress and progress.step("Generating podcast script")
        podcast_script = asyncio.run(
            generate_podcast_script_async(
                compressed_pdf_path,
                model=model,
                progress=progress,
                custom_instructions=custom_instructions,
                api_key=api_key,
            )
        )

        progress and progress.step("Generating audio")
    else:
        podcast_script = "This is a test of the audio system. It should be able to generate audio from a script."

    if save_script_locally:
        write_text_file(f"saved_outputs/{podcast_title}_{model}.txt", podcast_script)

    temp_file_name = generate_audio(
        podcast_title, podcast_script, audio_model, remote=remote
    )

    if save_audio_locally and temp_file_name:
        progress and progress.step("Saving audio locally")
        os.makedirs(local_output_path, exist_ok=True)

        file_extension = os.path.splitext(temp_file_name)[1]
        local_file_path = os.path.join(
            local_output_path, f"{podcast_title}{file_extension}"
        )
        shutil.copy2(temp_file_name, local_file_path)

        progress and progress.step(f"Audio saved to {local_file_path}")

    progress and progress.step("Done")
    return temp_file_name


if __name__ == "__main__":
    icloud_path = "/Users/derek/Library/Mobile Documents/com~apple~CloudDocs/Desktop/ML Papers 2/papers_to_read"
    pdf_name = "Reinforcement Learning Teachers of Test Time Scaling.pdf"
    custom_instructions = None
    # custom_instructions = """\
    # Pay special attention and care to the group relative policy optimization section. This should be the most important section of the podcast.
    # """
    pdf_path = os.path.join(icloud_path, pdf_name)
    temp_file = generate_entire_podcast(
        pdf_path,
        model="gemini-2.5-pro",
        audio_model="eleven_labs",
        remote=True,
        save_script_locally=True,
        save_audio_locally=True,
        custom_instructions=custom_instructions
    )

