from podcaist.model_garden import generate_text_response, generate_text_response_async
from podcaist.utils import format_contributions

prompt = """Attached is a pdf of a research paper. Here are what I think the main contributions are \
from the paper. I want you to dive into the results and answer the question of whether the results \
back up the authors claims. Dive deep into details about what metrics were used and show your \
thought process about whether these metrics are solid for the case at hand or if they leave something \
to be desired.

Here are the contributions listed:
{contributions}
"""



def results(
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


async def results_async(
    pdf_file_path: str, contributions: list[str], model: str = "gpt-4o-mini-2024-07-18", api_key: str | None = None
) -> str:
    formatted_contributions = format_contributions(contributions)
    input = [
        ("pdf", pdf_file_path),
        ("text", prompt.format(contributions=formatted_contributions)),
    ]
    response = await generate_text_response_async(input, model, api_key=api_key)
    return response
