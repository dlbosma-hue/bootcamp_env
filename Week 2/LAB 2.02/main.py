"""Main orchestrator for the Product Description Generator."""

import json
from typing import List, Optional

from openai import OpenAI

from config import AppConfig
from models import Product
from helpers import (
    create_product_prompt,
    format_output,
    load_json_file,
    parse_api_response,
    validate_product_data,
)


def load_and_validate_products(json_path: str) -> List[Product]:
    """Load JSON and validate products."""
    data = load_json_file(json_path)
    products = []
    for item in data.get("products", []):
        try:
            products.append(validate_product_data(item))
        except ValueError as exc:
            identifier = item.get("id") or item.get("name") or "<unknown>"
            print(f"[load_and_validate_products] Skipping product '{identifier}': {exc}")
    return products


def generate_description(product: Product, api_client, model: str = "gpt-4") -> str:
    """Generate description for one product using API."""
    prompt = create_product_prompt(product)
    try:
        response = api_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return parse_api_response(response)
    except Exception as exc:
        raise RuntimeError(
            f"[generate_description] API call failed for product '{product.id}': {exc}"
        ) from exc


def process_products(products: List[Product], api_client, model: str = "gpt-4") -> List[dict]:
    """Process all products and generate descriptions."""
    results = []
    for product in products:
        try:
            description = generate_description(product, api_client, model)
            results.append(format_output(product, description))
        except RuntimeError as exc:
            print(f"[process_products] Skipping product '{product.id}': {exc}")
    return results


def save_results(results: List[dict], output_path: str) -> None:
    """Save results to JSON file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"[save_results] Saved {len(results)} result(s) to {output_path}")
    except OSError as exc:
        raise OSError(
            f"[save_results] Could not write to '{output_path}': {exc}"
        ) from exc


def generate_product_descriptions(
    config: Optional[AppConfig] = None,
    client: Optional[OpenAI] = None,
) -> list[dict]:
    """Main orchestrator — delegates all real work to focused functions."""
    if config is None:
        config = AppConfig()

    # 1. Load & validate
    products = load_and_validate_products(config.input_file)
    if not products:
        print("[main] No valid products found. Nothing to do.")
        return []

    # 2. Generate descriptions via API
    if client is None:
        client = OpenAI(api_key=config.api_key)
    results = process_products(products, client, config.model)

    # 3. Persist
    save_results(results, config.output_file)

    return results


if __name__ == "__main__":
    generate_product_descriptions()
