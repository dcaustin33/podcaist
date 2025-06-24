import asyncio
import json
import os
import tempfile

from pydantic import BaseModel, Field

from podcaist.model_garden import generate_text_response, generate_text_response_async
from podcaist.pdf_utils import compress_pdf
from podcaist.utils import write_json_file

prompt = """
Based on the attached pdf I want you to summarize the key contributions of the paper. \
Specifically I want you to ask yourself why the research community should care about this paper. \
What exactly does it contribute to the field that was not known before. \
This can be multi-faceted and should likely be a list of possible reasons why we should care about the paper. \
Lastly detail the conclusions of the paper and what question it solved or answered.
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


if __name__ == "__main__":
    possible_models = [
        "gpt-4o-mini-2024-07-18",
        "o3-2025-04-16",
        "o3-mini-2025-01-31",
        "gpt-4.1-2025-04-14",
        "gemini-2.5-pro",
    ]
    model_name = possible_models[4]

    pdf_name = "Learning Physically Simulated Tennis Skills from Broadcast Videos.pdf"
    pdf_path = (
        "/Users/derek/Library/Mobile Documents/com~apple~CloudDocs/Desktop/ML Papers 2/papers_to_read/"
        + pdf_name
    )
    compressed_pdf_path = tempfile.NamedTemporaryFile(suffix=".pdf", delete=True).name
    compress_pdf(pdf_path, compressed_pdf_path)
    compressed_size = os.path.getsize(compressed_pdf_path)
    print(f"Compressed PDF size: {compressed_size / (1024*1024):.2f} MB")
    response = asyncio.run(
        summarize_contributions_async(compressed_pdf_path, model_name)
    )

    write_json_file(f"saved_outputs/contributions_{model_name}.json", response)
