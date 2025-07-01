import asyncio
import json
import os
from typing import Any, Dict, List, Optional

from google import genai
from google.genai.types import CreateCachedContentConfig, GenerateContentConfig, Part
from pydantic import BaseModel

from podcaist.utils import read_pdf_file_bytes

MODEL_TO_CACHED_TOKEN_PRICE = {
    "gemini-2.5-pro": 0.31,
    "gemini-2.5-flash": 0.075,
}

MODEL_TO_INPUT_PRICE_PER_MILLION = {
    "gemini-2.5-pro": 1.25,
    "gemini-2.5-flash": 0.3,
}

MODEL_TO_OUTPUT_PRICE_PER_MILLION = {
    "gemini-2.5-pro": 10,
    "gemini-2.5-flash": 2.5,
}


def get_gemini_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    return client


def get_pdf_for_prompt(pdf_path: str) -> bytes:
    pdf_bytes = read_pdf_file_bytes(pdf_path)
    return Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")


def upload_pdf_and_cache(
    pdf_path: str, model: str = "gemini-2.0-flash-lite-001"
) -> str:
    client = get_gemini_client()
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
    client = get_gemini_client()
    return client.caches.list()


def delete_cached_content(cache_name: str) -> None:
    client = get_gemini_client()
    client.caches.delete(cache_name)


def generate_price_estimate(
    model: str,
    input_tokens: int,
    cached_tokens: int,
    output_tokens: int,
    thoughts_tokens: int,
) -> float:
    input_tokens = 0 if input_tokens is None else input_tokens
    cached_tokens = 0 if cached_tokens is None else cached_tokens
    output_tokens = 0 if output_tokens is None else output_tokens
    thoughts_tokens = 0 if thoughts_tokens is None else thoughts_tokens
    input_price = (
        MODEL_TO_INPUT_PRICE_PER_MILLION[model]
        * (input_tokens - cached_tokens)
        / 1000000
    )
    cached_price = MODEL_TO_CACHED_TOKEN_PRICE[model] * cached_tokens / 1000000
    output_price = (
        MODEL_TO_OUTPUT_PRICE_PER_MILLION[model]
        * (output_tokens + thoughts_tokens)
        / 1000000
    )
    print(
        f" Total price: {input_price + cached_price + output_price}. Input price: {input_price}, cached price: {cached_price}, output price: {output_price}"
    )
    return input_price + cached_price + output_price


def generate_gemini_response(
    input_contents: list,
    model: str = "gemini-2.0-flash-lite-001",
    response_format: Optional[BaseModel] = None,
) -> str:
    client = get_gemini_client()

    config = None
    if response_format:
        config = GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_format,
        )
    resp = client.models.generate_content(
        model=model, contents=input_contents, config=config
    )
    # generate_price_estimate(
    #     model,
    #     resp.usage_metadata.prompt_token_count,
    #     resp.usage_metadata.cached_content_token_count,
    #     resp.usage_metadata.candidates_token_count,
    #     resp.usage_metadata.thoughts_token_count,
    # )

    return json.loads(resp.text) if response_format else resp.text


async def generate_gemini_response_async(
    input_contents: list,
    model: str = "gemini-2.0-flash-lite-001",
    response_format: Optional[BaseModel] = None,
) -> str | Dict[str, Any]:
    """Generate a response (optionally JSON‑parsed) asynchronously."""
    client = get_gemini_client()
    cfg = (
        GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=response_format,
        )
        if response_format
        else None
    )

    resp = await client.aio.models.generate_content(
        model=model,
        contents=input_contents,
        config=cfg,
    )
    # generate_price_estimate(
    #     model,
    #     resp.usage_metadata.prompt_token_count,
    #     resp.usage_metadata.cached_content_token_count,
    #     resp.usage_metadata.candidates_token_count,
    #     resp.usage_metadata.thoughts_token_count,
    # )
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