import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from data_processor import DataProcessor
from llm_processor import LLMProcessor
from tts_generator import TTSGenerator

# Initialize processors
data_processor = DataProcessor()
llm_processor = LLMProcessor()
tts_generator = TTSGenerator()

# FastAPI app
app = FastAPI()

# Allow Gradio frontend to talk to FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
#   PODCAST PIPELINE FUNCTION
# -------------------------------
def generate_podcast_pipeline(text_input, pdf_file):
    try:
        if pdf_file:
            # Extract the actual file path
            if hasattr(pdf_file, "name"):
                pdf_path = pdf_file.name
            elif isinstance(pdf_file, dict) and "name" in pdf_file:
                pdf_path = pdf_file["name"]
            else:
                pdf_path = pdf_file  # fallback for string paths

            processed = data_processor.process_pdf(pdf_path)

        else:
            processed = data_processor.process_text_input(text_input)

        script = llm_processor.generate_podcast_script(processed)
        audio_path = tts_generator.text_to_speech(script)

        return script, audio_path

    except Exception as e:
        return f"Error: {str(e)}", None


# -------------------------------
#   GRADIO INTERFACE
# -------------------------------
def gradio_interface(text_input, pdf_file):
    return generate_podcast_pipeline(text_input, pdf_file)


with gr.Blocks(title="Podcast Studio") as gradio_app:
    gr.Markdown("# 🎙️ Podcast Studio\nGenerate podcasts from text or PDF")

    text_input = gr.Textbox(label="Enter text", placeholder="Type your content here...")
    pdf_input = gr.File(label="Upload PDF", file_types=[".pdf"])

    generate_btn = gr.Button("Generate Podcast")

    script_output = gr.Textbox(label="Generated Script")
    audio_output = gr.Audio(label="Generated Audio", type="filepath")

    generate_btn.click(
        fn=gradio_interface,
        inputs=[text_input, pdf_input],
        outputs=[script_output, audio_output]
    )


# Mount Gradio inside FastAPI
@app.get("/")
def home():
    return {"message": "Podcast Studio API running"}


app = gr.mount_gradio_app(app, gradio_app, path="/gradio")


# -------------------------------
#   RUN SERVER
# -------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)