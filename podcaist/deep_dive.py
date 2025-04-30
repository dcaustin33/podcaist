from podcaist.model_garden import (generate_text_response,
                                   generate_text_response_async)

prompt = """
I have attached a pdf of a research paper where I have highlighted a certain contribution that I want 
you to explain in full full detail. This is intended for a podcast and for the listener to fully grasp 
the concept at hand. Do not spare any details.

A summary of the paper is:
{summary}

The contribution is:
{contribution}

Ensure that your response is thorough and explains any innovations they made, exactly how they did it, 
why they are important, if they build on previous work and any other details you determine are relevant.
"""


def deep_dive_contribution(
    pdf_file_path: str,
    contribution: str,
    summary: str,
    model: str = "gpt-4o-mini-2024-07-18",
) -> str:
    input = [
        ("pdf", pdf_file_path),
        ("text", prompt.format(contribution=contribution, summary=summary)),
    ]

    response = generate_text_response(
        input_contents=input,
        model=model,
    )
    return response


def format_deep_dives(deep_dive_output: list[str]) -> str:
    final_output = ""
    for idx, output in enumerate(deep_dive_output):
        final_output += f"Deep Dive {idx + 1}:\n{output}\n\n"
    return final_output


async def deep_dive_contribution_async(
    pdf_file_path: str,
    contribution: str,
    summary: str,
    model: str = "gpt-4o-mini-2024-07-18",
) -> str:
    input = [
        ("pdf", pdf_file_path),
        ("text", prompt.format(contribution=contribution, summary=summary)),
    ]
    response = await generate_text_response_async(input, model)
    return response
