from podcaist.model_garden import (generate_text_response,
                                   generate_text_response_async)

prompt = """Attached is a pdf of a research paper. I want you to truly understand the exact methods \
in which the authors have implemented their contributions. Please describe in painstaking detail \
exactly what architectures they have used, parameters, models, datasets, etc. I want you to be \
extremely specific and as long winded as needed so I could implement this method myself just from your description.

Show your thought process and reasoning for each step and do not be afraid to be long winded.
"""


def method(pdf_file_path: str, model: str = "gpt-4o-mini-2024-07-18") -> str:
    input = [("pdf", pdf_file_path), ("text", prompt)]
    response = generate_text_response(
        input_contents=input,
        model=model,
    )
    return response


async def method_async(
    pdf_file_path: str, model: str = "gpt-4o-mini-2024-07-18"
) -> str:
    input = [("pdf", pdf_file_path), ("text", prompt)]
    response = await generate_text_response_async(input, model)
    return response
