import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI, OpenAI
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
) -> Dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    if response_format:
        completion = client.beta.chat.completions.parse(
            model=model, messages=input_contents, response_format=response_format
        )
        return json.loads(completion.choices[0].message.parsed.model_dump_json())
    else:
        completion = client.chat.completions.create(
            model=model, messages=input_contents
        )
        return completion.choices[0].message.content


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
) -> Dict[str, Any] | str:
    """
    Async wrapper around the OpenAI chat endpoint.

    • If `response_format` is a Pydantic model, we call the *structured‑output* beta
      helper and return the parsed dict.
    • Otherwise we return the raw string content.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    client = AsyncOpenAI(api_key=api_key)
    if response_format:
        completion = await client.beta.chat.completions.parse(
            model=model,
            messages=input_contents,
            response_format=response_format,
        )
        parsed = completion.choices[0].message.parsed
        # `parsed` is a Pydantic object; convert to dict then JSON‑safe str/dict.
        return json.loads(parsed.model_dump_json())
    else:
        completion = await client.chat.completions.create(
            model=model,
            messages=input_contents,
        )
        return completion.choices[0].message.content


async def main():
    prompts = [
        [{"role": "user", "content": "Summarise HTTP/3 in one tweet."}],
        [{"role": "user", "content": "Name three uses for AsyncIO."}],
    ]
    tasks = [generate_openai_response_async(p) for p in prompts]
    for prompt, reply in zip(prompts, await asyncio.gather(*tasks)):
        print(prompt[0]["content"], "→", reply)
