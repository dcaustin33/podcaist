import asyncio
import os
import tempfile

from podcaist.ablation_studies import ablation_studies, ablation_studies_async
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
) -> str:

    progress and progress.step("Summarizing the main contributions")
    contributions = summarize_contributions(pdf_file_path=pdf_file_path, model=model)

    limitation_text = limitations(pdf_file_path, contributions, model)
    results_text = results(pdf_file_path, contributions, model)
    method_text = method(pdf_file_path, contributions, model)

    podcast = generate_podcast(
        pdf_file_path, contributions, method_text, results_text, limitation_text, model
    )
    if write_output:
        write_text_file(f"saved_outputs/podcast_{model}.txt", podcast)
    return podcast


async def generate_podcast_script_async(
    pdf_file_path: str,
    model="gpt-4o-mini-2024-07-18",
    write_output: bool = False,
    progress: Progress | None = None,
) -> str:

    progress and progress.step("Summarizing the main contributions")
    contributions = await summarize_contributions_async(
        pdf_file_path=pdf_file_path, model=model
    )

    # Run these three operations concurrently
    limitation_text, results_text, method_text = await asyncio.gather(
        limitations_async(pdf_file_path, contributions, model),
        results_async(pdf_file_path, contributions, model),
        method_async(pdf_file_path, contributions, model),
    )

    podcast = generate_podcast(
        pdf_file_path, contributions, method_text, results_text, limitation_text, model
    )
    if write_output:
        write_text_file(f"saved_outputs/podcast_{model}.txt", podcast)
    return podcast


if __name__ == "__main__":
    possible_models = ["o3-2025-04-16", "gemini-2.5-pro"]
    model = possible_models[0]
    pdf_name = "Evolutionary Policy Optimization.pdf"
    pdf_path = (
        "/Users/derek/Library/Mobile Documents/com~apple~CloudDocs/Desktop/ML Papers 2/papers_to_read/"
        + pdf_name
    )
    compressed_pdf_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=True).name
    compress_pdf(pdf_path, compressed_pdf_path)
    generate_podcast_script(compressed_pdf_path, model=model, write_output=True)
