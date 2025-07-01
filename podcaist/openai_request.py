import asyncio
import json
import os
import time
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI, OpenAI, RateLimitError
from pydantic import BaseModel


def create_file(file_path: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    file = client.files.create(file=open(file_path, "rb"), purpose="user_data")
    return file.id


def list_uploaded_files() -> List[Dict[str, Any]]:
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    files = client.files.list()
    return {f"{file.filename}": file.id for file in files}


def generate_openai_response(
    input_contents: list,
    model: str = "gpt-4o-mini-2024-07-18",
    response_format: Optional[BaseModel] = None,
    api_key: str | None = None,
) -> Dict[str, Any]:
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    max_retries = 5
    base_delay = 1  # Start with 1 second

    for attempt in range(max_retries):
        try:
            if response_format:
                completion = client.beta.chat.completions.parse(
                    model=model,
                    messages=input_contents,
                    response_format=response_format,
                )
                return json.loads(
                    completion.choices[0].message.parsed.model_dump_json()
                )
            else:
                completion = client.chat.completions.create(
                    model=model, messages=input_contents
                )
                return completion.choices[0].message.content

        except RateLimitError:
            if attempt == max_retries - 1:  # Last attempt
                raise  # Re-raise the last error if we're out of retries

            delay = base_delay * (2**attempt)  # 1, 2, 4, 8, 16 seconds
            time.sleep(delay)
            continue


def find_file_by_name(file_name: str) -> str:
    all_files = list_uploaded_files()
    for file in all_files:
        if file_name in file:
            return all_files[file]
    return None


def get_file_id(file_path: str) -> str:
    file_id = find_file_by_name(file_path.split("/")[-1])
    if file_id is None:
        file_id = create_file(file_path)
    return file_id


def delete_file(file_id: str) -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    client.files.delete(file_id)


async def generate_openai_response_async(
    input_contents: list,
    model: str = "gpt-4o-mini-2024-07-18",
    response_format: Optional[BaseModel] = None,
    api_key: str | None = None,
) -> Dict[str, Any] | str:
    """
    Async wrapper around the OpenAI chat endpoint.

    • If `response_format` is a Pydantic model, we call the *structured‑output* beta
      helper and return the parsed dict.
    • Otherwise we return the raw string content.
    • Implements exponential backoff for rate limit errors (429)
    """
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
        
    client = AsyncOpenAI(api_key=api_key)

    max_retries = 5
    base_delay = 1  # Start with 1 second

    for attempt in range(max_retries):
        try:
            if response_format:
                completion = await client.beta.chat.completions.parse(
                    model=model,
                    messages=input_contents,
                    response_format=response_format,
                )
                parsed = completion.choices[0].message.parsed
                return json.loads(parsed.model_dump_json())
            else:
                completion = await client.chat.completions.create(
                    model=model,
                    messages=input_contents,
                )
                return completion.choices[0].message.content

        except RateLimitError:
            if attempt == max_retries - 1:  # Last attempt
                raise  # Re-raise the last error if we're out of retries

            delay = base_delay * (2**attempt)  # 1, 2, 4, 8, 16 seconds
            await asyncio.sleep(delay)
            continue
