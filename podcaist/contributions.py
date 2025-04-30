from pydantic import BaseModel, Field

from podcaist.model_garden import (generate_text_response,
                                   generate_text_response_async)

prompt = """
Based on the attach pdf I want you to summarize the key contributions of the paper. 
Specifically I want you to identify how this paper moves the field forward. 
This can be multi-faceted as well - it does not have to be a single contribution. 
For instance, you should identify if the paper uses a new loss function, a new model, a new dataset, a new evaluation metric, or a new application of a known method.
"""


class Contributions(BaseModel):
    summary: str = Field(
        description="A concise summary of all the contributions combined into a single paragraph"
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
