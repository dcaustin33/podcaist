import asyncio
import json
from typing import Any, Dict, List, Optional

from google import genai
from google.genai.types import (CreateCachedContentConfig,
                                GenerateContentConfig, Part)
from pydantic import BaseModel

from podcaist.api_secrets import gemini_api_key
from podcaist.utils import read_pdf_file_bytes

client = genai.Client(api_key=gemini_api_key)
aio = client.aio


def get_pdf_for_prompt(pdf_path: str) -> bytes:
    pdf_bytes = read_pdf_file_bytes(pdf_path)
    return Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")


def upload_pdf_and_cache(
    pdf_path: str, model: str = "gemini-2.0-flash-lite-001"
) -> str:
    client = genai.Client(api_key=gemini_api_key)
    pdf_bytes = read_pdf_file_bytes(pdf_path)
    client_pdf_type = Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
    document = client.files.upload(
        file=client_pdf_type, config=dict(mime_type="application/pdf")
    )
    cache = client.caches.create(
        model=model,
        config=CreateCachedContentConfig(
            system_instruction="You are an expert AI podcast host explaining a research paper to a general but tech-curious audience.",
            contents=[document],
        ),
    )
    return cache


def list_cached_content() -> List[Dict[str, Any]]:
    client = genai.Client(api_key=gemini_api_key)
    return client.caches.list()


def delete_cached_content(cache_name: str) -> None:
    client = genai.Client(api_key=gemini_api_key)
    client.caches.delete(cache_name)


def generate_gemini_response(
    input_contents: list,
    model: str = "gemini-2.0-flash-lite-001",
    response_format: Optional[BaseModel] = None,
) -> str:
    client = genai.Client(api_key=gemini_api_key)

    config = None
    if response_format:
        config = GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_format,
        )

    output = client.models.generate_content(
        model=model, contents=input_contents, config=config
    )

    return json.loads(output.text) if response_format else output.text


async def generate_gemini_response_async(
    input_contents: list,
    model: str = "gemini-2.0-flash-lite-001",
    response_format: Optional[BaseModel] = None,
) -> str | Dict[str, Any]:
    """Generate a response (optionally JSON‑parsed) asynchronously."""
    cfg = (
        GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_format,
        )
        if response_format
        else None
    )

    resp = await aio.models.generate_content(
        model=model,
        contents=input_contents,
        config=cfg,
    )
    return json.loads(resp.text) if response_format else resp.text


async def main() -> None:
    # Fire off several requests in parallel
    prompts = [
        "Explain retro‐propulsion landing in 2 sentences.",
        "Why do NAND flash cells wear out?",
        "Give me a Python one‑liner to flatten a nested list.",
    ]
    tasks = [generate_gemini_response_async(p) for p in prompts]
    for prompt, reply in zip(prompts, await asyncio.gather(*tasks)):
        print(f"{prompt}\n→ {reply}\n")