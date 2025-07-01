from typing import Callable, Optional

from pydantic import BaseModel

from podcaist.gemini_request import (generate_gemini_response,
                                     generate_gemini_response_async,
                                     get_pdf_for_prompt)
from podcaist.openai_request import (generate_openai_response,
                                     generate_openai_response_async,
                                     get_file_id)

MODEL_TO_PROVIDER_MAP = {
    "gpt-4o-mini-2024-07-18": "openai",
    "o3-2025-04-16": "openai",
    "o3-mini-2025-01-31": "openai",
    "gpt-4.1-2025-04-14": "openai",
    "gemini-2.5-pro": "google",
    "gemini-2.5-flash": "google",
    "gemini-2.0-flash-001": "google",
    "gemini-2.0-flash-lite-001": "google",
}

PROVIDER_TO_FUNCTION_MAP = {
    "openai": generate_openai_response,
    "google": generate_gemini_response,
}

PROVIDER_TO_FUNCTION_MAP_ASYNC = {
    "openai": generate_openai_response_async,
    "google": generate_gemini_response_async,
}


def get_provider(model: str) -> str:
    return MODEL_TO_PROVIDER_MAP[model]


def get_function(provider: str, async_mode: bool = False) -> Callable:
    return (
        PROVIDER_TO_FUNCTION_MAP[provider]
        if not async_mode
        else PROVIDER_TO_FUNCTION_MAP_ASYNC[provider]
    )


def get_function_for_model(model: str, async_mode: bool = False) -> Callable:
    return get_function(get_provider(model), async_mode)


def generate_text_response(
    input_contents: list[tuple[str, str]],
    model: str = "gpt-4o-mini-2024-07-18",
    response_format: Optional[BaseModel] = None,
) -> str:
    """Input contents should be a dict with the type (pdf or text) and then the actual content

    If the type is pdf it should be the path to the pdf file.
    """
    assert (
        len(input_contents) <= 2
    ), "Only one pdf and one text input is supported currently"
    assert (
        input_contents[0][0] == "pdf" or input_contents[0][0] == "text"
    ), "The first input should be the path to the pdf file or the text"
    formatted_input_contents = generate_input_contents(input_contents, model)
    return get_function_for_model(model)(
        formatted_input_contents, model, response_format
    )


def generate_input_contents(
    input_contents: list[tuple[str, str]],
    model: str = "gpt-4o-mini-2024-07-18",
) -> list:
    provider = get_provider(model)
    if provider == "openai":
        return generate_openai_input_contents(input_contents)
    elif provider == "google":
        return generate_gemini_input_contents(input_contents)
    else:
        raise ValueError("Invalid provider")


def generate_openai_input_contents(
    input_contents: list[tuple[str, str]],
) -> list:
    if len(input_contents) == 1:
        input_contents = [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": input_contents[0][1]}],
            }
        ]
        return input_contents
    elif len(input_contents) == 2:
        file_id = get_file_id(input_contents[0][1])
        input_contents = [
            {
                "role": "user",
                "content": [
                    {"type": "file", "file": {"file_id": file_id}},
                    {"type": "text", "text": input_contents[1][1]},
                ],
            }
        ]
        return input_contents
    else:
        raise ValueError("Invalid number of input contents")


def generate_gemini_input_contents(
    input_contents: list[tuple[str, str]],
) -> list:
    if len(input_contents) == 1:
        return [input_contents[0][1]]
    elif len(input_contents) == 2:
        pdf_file_bytes = get_pdf_for_prompt(input_contents[0][1])
        return [pdf_file_bytes, input_contents[1][1]]
    else:
        raise ValueError("Invalid number of input contents")


async def generate_text_response_async(
    input_contents: list[tuple[str, str]],
    model: str = "gpt-4o-mini-2024-07-18",
    response_format: Optional[BaseModel] = None,
) -> str:
    assert (
        len(input_contents) <= 2
    ), "Only one pdf and one text input is supported currently"
    assert (
        input_contents[0][0] == "pdf" or input_contents[0][0] == "text"
    ), "The first input should be the path to the pdf file or the text"
    formatted_input_contents = generate_input_contents(input_contents, model)
    output_function = get_function_for_model(model, True)
    output = await output_function(formatted_input_contents, model, response_format)
    return output
