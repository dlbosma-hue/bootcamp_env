"""Helper functions for loading, validating, prompting, parsing, and formatting."""

import json
from collections.abc import Mapping
from json import JSONDecodeError
from pathlib import Path

from pydantic import ValidationError

from models import Product


def load_json_file(file_path: str) -> dict:
    """Load and parse a JSON file, raising clear errors on failure."""
    path = Path(file_path)
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"[load_json_file] FileNotFoundError - Location: '{file_path}' not found."
            f" Suggestion: verify the path and file permissions."
        ) from exc
    except JSONDecodeError as exc:
        raise ValueError(
            f"[load_json_file] JSONDecodeError - Location: '{file_path}' (line {exc.lineno}, column {exc.colno})."
            f" Message: {exc.msg}. Suggestion: fix the JSON syntax around the reported line."
        ) from exc


def validate_product_data(product_dict: dict) -> Product:
    """Validate a raw dict against the Product schema."""
    try:
        return Product(**product_dict)
    except ValidationError as exc:
        error_details = "; ".join(
            f"{'.'.join(str(part) for part in err['loc'])}: {err['msg']}"
            for err in exc.errors()
        )
        identifier = product_dict.get("id", "<unknown>")
        raise ValueError(
            f"[validate_product_data] ValidationError - Product ID: '{identifier}'."
            f" Details: {error_details}. Suggestion: fix the listed fields and retry."
        ) from exc


def create_product_prompt(product: Product) -> str:
    """Build the LLM prompt for a single product."""
    features = ", ".join(product.features) if product.features else "No features provided"
    return (
        f"Create a product description for:\n"
        f"Name: {product.name}\n"
        f"Category: {product.category}\n"
        f"Price: ${product.price:.2f}\n"
        f"Features: {features}\n\n"
        f"Generate a compelling product description."
    )


def parse_api_response(response) -> str:
    """Extract the text content from an OpenAI-style response (object or dict)."""
    choices = getattr(response, "choices", None)
    if choices is None and isinstance(response, Mapping):
        choices = response.get("choices")
    if not choices:
        raise ValueError("Response did not return any choices.")

    first_choice = choices[0]
    message = getattr(first_choice, "message", None)
    if message is None and isinstance(first_choice, Mapping):
        message = first_choice.get("message")
    if message is None:
        raise ValueError("First choice missing 'message'.")

    content = getattr(message, "content", None)
    if content is None and isinstance(message, Mapping):
        content = message.get("content")
    if not isinstance(content, str):
        raise ValueError("Message content is missing or not textual.")

    return content.strip()


def format_output(product: Product, description: str) -> dict:
    """Build the final output dict for one product."""
    return {
        "product_id": product.id,
        "name": product.name,
        "description": description.strip(),
    }
