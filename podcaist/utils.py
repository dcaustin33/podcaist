import base64
import json


def convert_pdf_to_base64(pdf_path: str) -> str:
    with open(pdf_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode("utf-8")


def read_json_file(file_path: str) -> dict:
    with open(file_path, "r") as f:
        return json.load(f)


def write_json_file(file_path: str, data: dict) -> None:
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def write_text_file(file_path: str, data: str) -> None:
    with open(file_path, "w") as f:
        f.write(data)


def read_text_file(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()


def format_podcast(sections: tuple[str, str]) -> str:
    return "\n".join([section[1] for section in sections])


def read_pdf_file_bytes(file_path: str) -> bytes:
    with open(file_path, "rb") as f:
        return f.read()
