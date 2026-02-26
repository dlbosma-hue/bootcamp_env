# LAB M1.05 - Product Listing Generator (API Integration)

## Use Case
Generate product descriptions for an e-commerce store by sending product images to OpenAI's vision API and receiving structured marketing copy back.

## Key Concepts
- Base64 image encoding to send images via API
- OpenAI vision API call with image + text prompt
- Saving API responses as JSON output files

## Core Helper Functions
- `encode_image(image_path)` - converts an image file to base64 string for API transmission
- `create_prompt(product_name, category)` - builds a structured prompt for generating a product description
- `call_openai_api(image_b64, prompt)` - makes the API request and returns the response
- `save_output(data, filename)` - writes the result to a JSON file

## Pattern
All labs follow the same universal structure:
1. Imports at the top
2. All function definitions
3. Data / configuration setup
4. Function calls and usage

---

# LAB M1.07 - Whisper Audio Transcription

## Use Case
Transcribe audio recordings using OpenAI's Whisper model and export clean text transcripts.

## Key Concepts
- Loading audio files in Python (wav, mp3)
- Splitting long audio into chunks to stay within API limits
- Calling Whisper transcription API per chunk
- Joining chunk results and exporting the full transcript

## Core Helper Functions
- `load_audio(filepath)` - loads the audio file and returns duration info
- `split_audio(audio, chunk_length_ms)` - splits audio into smaller pieces using pydub
- `transcribe_chunk(chunk)` - sends one audio chunk to Whisper and returns text
- `export_transcript(text, output_path)` - saves the full joined transcript to a text file

## Key Learning
Whisper has a file size limit per API call. Splitting audio into chunks first and then transcribing each one separately is the standard workaround. Always define chunk size based on the API's token or file size limit, not arbitrary numbers.
