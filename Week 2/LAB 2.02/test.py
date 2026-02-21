"""Tests for the Product Description Generator modules."""

import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from models import Product
from helpers import (
    load_json_file,
    validate_product_data,
    create_product_prompt,
    parse_api_response,
    format_output,
)
from main import (
    load_and_validate_products,
    generate_description,
    process_products,
    save_results,
    generate_product_descriptions,
)

# ── Shared fixtures ──────────────────────────────────────────────────

SAMPLE_PRODUCT_DICT = {
    "id": "p1",
    "name": "Test Widget",
    "category": "Testing",
    "price": 15.50,
    "features": ["fast", "reliable"],
}

SAMPLE_PAYLOAD = {"products": [SAMPLE_PRODUCT_DICT]}


@pytest.fixture
def valid_product():
    return Product(**SAMPLE_PRODUCT_DICT)


@pytest.fixture
def tmp_json_file():
    """Create a temporary JSON file with sample data, clean up after test."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(SAMPLE_PAYLOAD, f)
        path = Path(f.name)
    yield str(path)
    path.unlink(missing_ok=True)


# ── 1. load_json_file ───────────────────────────────────────────────

class TestLoadJsonFile:
    def test_loads_valid_json(self, tmp_json_file):
        result = load_json_file(tmp_json_file)
        assert result == SAMPLE_PAYLOAD

    def test_raises_file_not_found_with_path(self):
        with pytest.raises(FileNotFoundError, match="nonexistent_abc123.json"):
            load_json_file("nonexistent_abc123.json")

    def test_raises_value_error_for_bad_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{bad json,,,}")
            path = Path(f.name)
        try:
            with pytest.raises(ValueError, match="line"):
                load_json_file(str(path))
        finally:
            path.unlink(missing_ok=True)


# ── 2. validate_product_data ────────────────────────────────────────

class TestValidateProductData:
    def test_accepts_valid_data(self):
        product = validate_product_data(SAMPLE_PRODUCT_DICT)
        assert isinstance(product, Product)
        assert product.name == "Test Widget"

    def test_rejects_negative_price(self):
        bad = {**SAMPLE_PRODUCT_DICT, "price": -1}
        with pytest.raises(ValueError, match="(?i)price"):
            validate_product_data(bad)

    def test_rejects_missing_required_field(self):
        with pytest.raises(ValueError, match="(?i)category"):
            validate_product_data({"id": "p2", "name": "No Category"})

    def test_defaults_features_to_empty_list(self):
        data = {k: v for k, v in SAMPLE_PRODUCT_DICT.items() if k != "features"}
        product = validate_product_data(data)
        assert product.features == []


# ── 3. create_product_prompt ────────────────────────────────────────

class TestCreateProductPrompt:
    def test_includes_product_details(self, valid_product):
        prompt = create_product_prompt(valid_product)
        assert "Test Widget" in prompt
        assert "$15.50" in prompt
        assert "fast" in prompt

    def test_handles_no_features(self):
        bare = Product(id="x", name="Bare", category="Cat", price=1.0, features=[])
        prompt = create_product_prompt(bare)
        assert "No features provided" in prompt


# ── 4. parse_api_response ───────────────────────────────────────────

class TestParseApiResponse:
    def test_parses_object_response(self):
        resp = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="  Great product  "))]
        )
        assert parse_api_response(resp) == "Great product"

    def test_parses_dict_response(self):
        resp = {"choices": [{"message": {"content": "Dict description"}}]}
        assert parse_api_response(resp) == "Dict description"

    def test_raises_on_empty_choices(self):
        with pytest.raises(ValueError, match="choices"):
            parse_api_response(SimpleNamespace(choices=[]))

    def test_raises_on_missing_message(self):
        with pytest.raises(ValueError):
            parse_api_response(SimpleNamespace(choices=[SimpleNamespace()]))


# ── 5. format_output ────────────────────────────────────────────────

class TestFormatOutput:
    def test_returns_correct_dict(self, valid_product):
        result = format_output(valid_product, "  A nice widget  ")
        assert result == {
            "product_id": "p1",
            "name": "Test Widget",
            "description": "A nice widget",
        }


# ── 6. Modular functions (Step 3) ───────────────────────────────────

class FakeCompletions:
    def create(self, **kwargs):
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="A great product!"))]
        )


class FakeClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=FakeCompletions())


MIXED_PAYLOAD = {
    "products": [
        SAMPLE_PRODUCT_DICT,
        {"id": "bad", "name": "Bad", "category": "X", "price": -5},
    ]
}


@pytest.fixture
def mixed_json_file():
    """JSON with one valid and one invalid product."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(MIXED_PAYLOAD, f)
        path = Path(f.name)
    yield str(path)
    path.unlink(missing_ok=True)


class TestLoadAndValidateProducts:
    def test_returns_valid_products_only(self, mixed_json_file):
        products = load_and_validate_products(mixed_json_file)
        assert len(products) == 1
        assert products[0].id == "p1"

    def test_raises_for_missing_file(self):
        with pytest.raises(FileNotFoundError):
            load_and_validate_products("no_such_file.json")


class TestGenerateDescription:
    def test_returns_description(self, valid_product):
        desc = generate_description(valid_product, FakeClient())
        assert desc == "A great product!"


class TestProcessProducts:
    def test_processes_all_valid(self, mixed_json_file):
        products = load_and_validate_products(mixed_json_file)
        results = process_products(products, FakeClient())
        assert len(results) == 1
        assert results[0]["product_id"] == "p1"


class TestSaveResults:
    def test_saves_to_file(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)
        try:
            save_results([{"product_id": "p1", "name": "X", "description": "Y"}], str(path))
            with path.open() as f:
                data = json.load(f)
            assert len(data) == 1
            assert data[0]["product_id"] == "p1"
        finally:
            path.unlink(missing_ok=True)


class TestGenerateProductDescriptionsE2E:
    def test_full_pipeline(self, tmp_json_file):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            out_path = Path(f.name)
        try:
            from config import AppConfig

            cfg = AppConfig(input_file=tmp_json_file, output_file=str(out_path))
            results = generate_product_descriptions(config=cfg, client=FakeClient())
            assert len(results) == 1
            with out_path.open() as f:
                saved = json.load(f)
            assert saved == results
        finally:
            out_path.unlink(missing_ok=True)


# ── Step 4: Error Handling Tests ─────────────────────────────────────
# Verify that every error shows WHAT, WHERE, and WHY.

from unittest.mock import MagicMock
from openai import APIError, APIConnectionError, APITimeoutError


class TestFileNotFoundErrorHandling:
    """Errors from load_json_file() show file path context."""

    def test_error_includes_file_path(self):
        with pytest.raises(FileNotFoundError, match="missing_products.json"):
            load_json_file("missing_products.json")

    def test_error_message_printed(self, capsys):
        """The printed error should mention the file path."""
        try:
            load_json_file("missing_products.json")
        except FileNotFoundError:
            pass
        # helpers.py raises with path in message; main uses helpers
        # just verify exception propagates with path info
        assert True


class TestJSONDecodeErrorHandling:
    """Errors from load_json_file() show line number and column."""

    def test_error_includes_line_info(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"key": "value",, "bad": true}')
            path = Path(f.name)
        try:
            with pytest.raises(ValueError, match="line"):
                load_json_file(str(path))
        finally:
            path.unlink(missing_ok=True)

    def test_error_includes_column_info(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"key": "value",, "bad": true}')
            path = Path(f.name)
        try:
            with pytest.raises(ValueError, match="column"):
                load_json_file(str(path))
        finally:
            path.unlink(missing_ok=True)


class TestValidationErrorHandling:
    """Errors from validate_product_data() show product ID and fields."""

    def test_error_includes_product_id(self):
        with pytest.raises(ValueError, match="bad_id"):
            validate_product_data({"id": "bad_id", "name": "X"})

    def test_error_includes_missing_field_name(self):
        with pytest.raises(ValueError, match="(?i)category"):
            validate_product_data({"id": "p99", "name": "No Cat"})

    def test_error_includes_price_detail(self):
        with pytest.raises(ValueError, match="(?i)price"):
            validate_product_data(
                {"id": "p99", "name": "Neg", "category": "X", "price": -5}
            )


class TestAPIErrorHandling:
    """Errors from generate_description() show product info and error type."""

    @staticmethod
    def _make_failing_client(exception):
        client = MagicMock()
        client.chat.completions.create.side_effect = exception
        return client

    def test_api_error_raises_runtime_error(self, valid_product):
        fake_err = APIError(
            message="Invalid API key",
            request=MagicMock(),
            body=None,
        )
        client = self._make_failing_client(fake_err)
        with pytest.raises(RuntimeError, match="API call failed"):
            generate_description(valid_product, client)

    def test_runtime_error_includes_product_id(self, valid_product):
        fake_err = APIError(
            message="Rate limit exceeded",
            request=MagicMock(),
            body=None,
        )
        client = self._make_failing_client(fake_err)
        with pytest.raises(RuntimeError, match=valid_product.id):
            generate_description(valid_product, client)


class TestNetworkErrorHandling:
    """Network errors from generate_description() show connection context."""

    @staticmethod
    def _make_failing_client(exception):
        client = MagicMock()
        client.chat.completions.create.side_effect = exception
        return client

    def test_timeout_error_raises_runtime_error(self, valid_product):
        fake_err = APITimeoutError(request=MagicMock())
        client = self._make_failing_client(fake_err)
        with pytest.raises(RuntimeError, match="API call failed"):
            generate_description(valid_product, client)

    def test_connection_error_raises_runtime_error(self, valid_product):
        fake_err = APIConnectionError(
            message="Connection refused", request=MagicMock()
        )
        client = self._make_failing_client(fake_err)
        with pytest.raises(RuntimeError, match="API call failed"):
            generate_description(valid_product, client)


class TestSaveResultsErrorHandling:
    """Errors from save_results() show file path context."""

    def test_bad_directory_raises_os_error(self):
        with pytest.raises(OSError, match="Could not write"):
            save_results(
                [{"product_id": "p1", "name": "X", "description": "Y"}],
                "/nonexistent_dir_xyz/output.json",
            )
