from pydantic import BaseModel, Field

from podcaist.model_garden import generate_text_response, generate_text_response_async
from podcaist.pdf_utils import compress_pdf
from podcaist.utils import write_json_file

prompt = """
Based on the attached pdf I want you to summarize the key contributions of the paper. \
Specifically I want you to ask yourself why the research community should care about this paper. \
What exactly does it contribute to the field that was not known before. \
This can be multi-faceted and should likely be a list of possible reasons why we should care about the paper. \
Lastly detail the conclusions of the paper and what question it solved or answered.\
"""


class Contributions(BaseModel):
    thoughts: str = Field(
        description="A detailed thought process of why this paper is important."
    )
    why_should_we_care: str = Field(
        description="A detailed explanation of why the research community should care about this paper."
    )
    key_contributions: list[str] = Field(
        description="A list of strings, each representing a distinct contribution of the paper"
    )


def summarize_contributions(
    pdf_file_path: str, model: str = "gpt-4o-mini-2024-07-18"
) -> str:
    input_to_model = [("pdf", pdf_file_path), ("text", prompt)]
    response = generate_text_response(
        input_contents=input_to_model, model=model, response_format=Contributions
    )
    return response


def format_contributions(response: str) -> str:
    final_contributions = ""
    for idx, contribution in enumerate(response["key_contributions"]):
        final_contributions += f"Contribution {idx+1}: {contribution}\n"
    return final_contributions


async def summarize_contributions_async(
    pdf_file_path: str, model: str = "gpt-4o-mini-2024-07-18"
) -> str:
    input_to_model = [("pdf", pdf_file_path), ("text", prompt)]
    response = await generate_text_response_async(input_to_model, model, Contributions)
    return response
