import asyncio
import os
import tempfile

from podcaist.contributions import (
    summarize_contributions,
    summarize_contributions_async,
)
from podcaist.generate_sections import generate_podcast
from podcaist.limitations import limitations, limitations_async
from podcaist.method import method, method_async
from podcaist.pdf_utils import compress_pdf
from podcaist.progress import Progress
from podcaist.results import results, results_async
from podcaist.utils import (
    format_podcast,
    read_json_file,
    read_text_file,
    write_json_file,
    write_text_file,
)

SEM_LIMIT = 10


def generate_podcast_script(
    pdf_file_path: str,
    model="gpt-4o-mini-2024-07-18",
    write_output: bool = False,
    progress: Progress | None = None,
    custom_instructions: str | None = None,
    api_key: str | None = None,
) -> str:

    progress and progress.step("Summarizing the main contributions")
    contributions = summarize_contributions(
        pdf_file_path=pdf_file_path, model=model, api_key=api_key
    )

    limitation_text = limitations(pdf_file_path, contributions, model, api_key=api_key)
    results_text = results(pdf_file_path, contributions, model, api_key=api_key)
    method_text = method(pdf_file_path, contributions, model, api_key=api_key)

    podcast = generate_podcast(
        pdf_file_path,
        contributions,
        method_text,
        results_text,
        limitation_text,
        model,
        custom_instructions,
        api_key=api_key,
    )
    if write_output:
        write_text_file(f"saved_outputs/podcast_{model}.txt", podcast)
    return podcast


async def generate_podcast_script_async(
    pdf_file_path: str,
    model="gpt-4o-mini-2024-07-18",
    write_output: bool = False,
    progress: Progress | None = None,
    custom_instructions: str | None = None,
    api_key: str | None = None,
) -> str:

    progress and progress.step("Summarizing the main contributions")
    contributions = await summarize_contributions_async(
        pdf_file_path=pdf_file_path, model=model, api_key=api_key
    )

    # Run these three operations concurrently
    limitation_text, results_text, method_text = await asyncio.gather(
        limitations_async(pdf_file_path, contributions, model, api_key=api_key),
        results_async(pdf_file_path, contributions, model, api_key=api_key),
        method_async(pdf_file_path, contributions, model, api_key=api_key),
    )
    progress and progress.step("Generating podcast script")

    podcast = generate_podcast(
        pdf_file_path,
        contributions,
        method_text,
        results_text,
        limitation_text,
        model,
        custom_instructions,
        api_key=api_key,
    )
    if write_output:
        write_text_file(f"saved_outputs/podcast_{model}.txt", podcast)
    return podcast


if __name__ == "__main__":
    # possible_models = ["o3-2025-04-16", "gemini-2.5-pro"]

    model = "gemini-2.5-flash"
    api_key = os.getenv("GEMINI_API_KEY")
    pdf_name = "Evolutionary Policy Optimization.pdf"
    pdf_path = (
        "/Users/derek/Library/Mobile Documents/com~apple~CloudDocs/Desktop/ML Papers 2/papers_to_read/"
        + pdf_name
    )
    compressed_pdf_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=True).name
    compress_pdf(pdf_path, compressed_pdf_path)
    asyncio.run(
        generate_podcast_script_async(
            compressed_pdf_path, model=model, write_output=True, api_key=api_key
        )
    )
