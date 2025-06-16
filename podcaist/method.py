import asyncio

from podcaist.contributions import format_contributions
from podcaist.model_garden import generate_text_response, generate_text_response_async

prompt = """Attached is a pdf of a research paper as well as what I determined are the main contributions. \
I want you to dive deep into the method used to attain these contributions and results as well. \
I want to understand exactly what they did, assuming the audience is a person with a Master's in AI. \
At the end of your explanation I should have the necessary knowledge to sketch the pseudocode and \
explain the method to others. Explore whether the method relies on a theoretical understanding or \
empirical studies. The output should be \
understandable over audio, ie provide a explanation in plain english. Dive deep into the details \
of the method and aim to have a summary that if a human were to read it, they would be able to \
understand the method and how it contributed to the results. You do not have to go sequentially \
throught hte contributions as some of the method can contribute to multiple so instead aim \
for a holistic understand of the method.

Here are the contributions: 
{contributions}
"""


def method(
    pdf_file_path: str, contributions: dict, model: str = "gpt-4o-mini-2024-07-18"
) -> str:
    formatted_contributions = format_contributions(contributions)
    input = [
        ("pdf", pdf_file_path),
        ("text", prompt.format(contributions=formatted_contributions)),
    ]
    response = generate_text_response(
        input_contents=input,
        model=model,
    )
    return response


async def method_async(
    pdf_file_path: str, contributions: dict, model: str = "gpt-4o-mini-2024-07-18"
) -> str:
    formatted_contributions = format_contributions(contributions)
    input = [
        ("pdf", pdf_file_path),
        ("text", prompt.format(contributions=formatted_contributions)),
    ]
    response = await generate_text_response_async(input, model)
    return response
