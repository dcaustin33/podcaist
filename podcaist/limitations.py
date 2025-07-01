from podcaist.model_garden import generate_text_response, generate_text_response_async
from podcaist.utils import format_contributions

prompt = """Attached is a research paper that I am seeking a deeper understanding of. \
I want you to examine the authors stated contributions as well as the contributions listed below \
and decide whether any limitations to their approach of how they evaluated their method or if any \
of their claims are unsubstantiated. You do not have to be harsh but if there are holes in \
the paper I want you to point them out. Feel free to also not include any holes if you tink it is a \
great paper.

Here are the contributions: 
{contributions}
"""


def limitations(
    pdf_file_path: str, contributions: list[str], model: str = "gpt-4o-mini-2024-07-18", api_key: str | None = None
) -> str:
    formatted_contributions = format_contributions(contributions)
    input = [
        ("pdf", pdf_file_path),
        ("text", prompt.format(contributions=formatted_contributions)),
    ]
    response = generate_text_response(
        input_contents=input,
        model=model,
        api_key=api_key,
    )
    return response


async def limitations_async(
    pdf_file_path: str, contributions: list[str], model: str = "gpt-4o-mini-2024-07-18", api_key: str | None = None
) -> str:
    formatted_contributions = format_contributions(contributions)
    input = [
        ("pdf", pdf_file_path),
        ("text", prompt.format(contributions=formatted_contributions)),
    ]
    response = await generate_text_response_async(input, model, api_key=api_key)
    return response
