# LAB M1.02 - Refactoring with AI

## Use Case
Take messy, monolithic Python code for a product description generator and refactor it into professional, maintainable code. The guiding principle: "If something breaks, I need to know WHAT, WHERE and WHY, not just that it broke."

## Problems in the Original Code
- Silent failures using `except: pass` (errors disappear without warning)
- One giant function doing six different things at once
- No error handling for file operations or API calls
- Repeated code patterns (DRY violation)
- Hardcoded API keys in the script

## Refactoring Approach: Path 2 (refactor provided starter code)

### 6 Helper Functions Created
- `load_json_file(filepath)` - loads a JSON file with proper error handling
- `validate_product_data(product)` - checks required fields exist before processing
- `create_product_prompt(product)` - builds the prompt string for the API call
- `parse_api_response(response)` - extracts the text from OpenAI response safely
- `format_output(product, description)` - combines product data and generated text
- `save_json_file(data, filepath)` - saves output with error handling

### 4 Modular Functions Created
- `load_and_validate_products(filepath)` - combines loading + validation
- `generate_description(product)` - runs the full API call for one product
- `process_products(products)` - loops through all products and generates descriptions
- `generate_product_descriptions(input_path, output_path)` - the top-level orchestrator

## Key Principles Applied
- Single Responsibility Principle: each function does one thing only
- DRY: no repeated code blocks
- Proper error handling: every function raises a clear, specific error message
- No hardcoded secrets: API keys loaded from environment variables

## Testing
11 tests written covering happy path, error cases, edge cases, and integration testing.

## Key Metric Improvements
- Longest function: reduced from 32 lines to 8 lines
- Silent failures: eliminated completely
- Error types handled: 6+ with contextual messages
- Code reusability: 100% (all logic in importable functions)
