import asyncio
import os

from podcaist.ablation_studies import ablation_studies, ablation_studies_async
from podcaist.contributions import (
    summarize_contributions,
    summarize_contributions_async,
)
from podcaist.deep_dive import (
    deep_dive_contribution,
    deep_dive_contribution_async,
    format_deep_dives,
)
from podcaist.generate_sections import generate_section_by_section
from podcaist.method import method, method_async
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
    generate_again: bool = False,
    model: str = "gpt-4o-mini-2024-07-18",
    write_output: bool = False,
) -> str:
    if generate_again:
        contributions = summarize_contributions(pdf_file_path, model)
        if write_output:
            write_json_file(
                f"saved_outputs/contributions_summary_{model}.json", contributions
            )

        deep_dives = []
        for i in range(len(contributions["key_contributions"])):
            deep_dive = deep_dive_contribution(
                pdf_file_path,
                contributions["key_contributions"][i],
                contributions["summary"],
                model,
            )
            deep_dives.append(deep_dive)
            if write_output:
                write_text_file(f"saved_outputs/deep_dive_{i}_{model}.txt", deep_dive)

        deep_dive_output = format_deep_dives(deep_dives)

        results_text = results(pdf_file_path, model)
        if write_output:
            write_text_file(f"saved_outputs/results_{model}.txt", results_text)

        ablation_studies_text = ablation_studies(pdf_file_path, model=model)
        if write_output:
            write_text_file(
                f"saved_outputs/ablation_studies_{model}.txt", ablation_studies_text
            )

        method_text = method(pdf_file_path, model=model)
        if write_output:
            write_text_file(f"saved_outputs/method_{model}.txt", method_text)

        sections = generate_section_by_section(
            pdf_file_path,
            deep_dive_output,
            results_text,
            ablation_studies_text,
            method_text,
            start_generation=0,
            end_generation=7,
            model=model,
        )

        podcast_script = format_podcast(sections)
        if write_output:
            write_text_file(f"saved_outputs/podcast_script_{model}.txt", podcast_script)

        return podcast_script
    else:
        contributions = read_json_file(
            f"saved_outputs/contributions_summary_{model}.json"
        )

        deep_dives = []
        for i in range(len(contributions)):
            section = read_json_file(f"saved_outputs/section_{model}_{i}.json")
            deep_dives.append(section)

        deep_dive_output = format_deep_dives(deep_dives)

        results_text = read_text_file(f"saved_outputs/results_{model}.txt")
        ablation_studies_text = read_text_file(
            f"saved_outputs/ablation_studies_{model}.txt"
        )
        method_text = read_text_file(f"saved_outputs/method_{model}.txt")

        sections = []
        for i in range(7):
            section = read_json_file(f"saved_outputs/section_{model}_{i}.json")
            sections.append((section[0], section[1]))

        podcast_script = format_podcast(sections)
        if write_output:
            write_text_file(f"saved_outputs/podcast_script_{model}.txt", podcast_script)

        return podcast_script


async def generate_podcast_script_async(
    pdf_file_path: str,
    generate_again: bool = True,
    model="gpt-4o-mini-2024-07-18",
    write_output: bool = False,
    progress: Progress | None = None,
):
    assert generate_again, "generate_again must be True"
    sem = asyncio.Semaphore(SEM_LIMIT)

    progress and progress.step("Summarizing the main contributions")
    first_tasks = await asyncio.gather(
        summarize_contributions_async(pdf_file_path, model),
        results_async(pdf_file_path, model),
        ablation_studies_async(pdf_file_path, model),
        method_async(pdf_file_path, model),
    )
    contributions, results_text, ablation_text, method_text = first_tasks
    if write_output:
        write_json_file(f"saved_outputs/contributions_{model}.json", contributions)

    progress and progress.step("Diving deep on research details")
    deep_dives = await asyncio.gather(
        *(
            deep_dive_contribution_async(
                pdf_file_path, i, contributions["summary"], model
            )
            for i in contributions["key_contributions"]
        )
    )

    if write_output:
        write_text_file(
            f"saved_outputs/results_{model}_{pdf_file_path.split('/')[-1].split('.')[0]}.txt",
            results_text,
        )
        write_text_file(
            f"saved_outputs/ablation_{model}_{pdf_file_path.split('/')[-1].split('.')[0]}.txt",
            ablation_text,
        )
        write_text_file(
            f"saved_outputs/method_{model}_{pdf_file_path.split('/')[-1].split('.')[0]}.txt",
            method_text,
        )

    deep_dive_output = format_deep_dives(deep_dives)

    progress and progress.step("Generating podcast script")
    sections = generate_section_by_section(
        pdf_file_path,
        deep_dive_output,
        results_text,
        ablation_text,
        method_text,
        start_generation=0,
        end_generation=7,
        model=model,
        write_output=write_output,
    )

    script = format_podcast(sections)
    if write_output:
        output_path = f"saved_outputs/podcast_script_{model}_{pdf_file_path.split('/')[-1].split('.')[0]}.txt"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        write_text_file(output_path, script)
    return script
