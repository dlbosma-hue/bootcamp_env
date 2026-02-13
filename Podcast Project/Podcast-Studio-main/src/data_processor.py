# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false

import fitz
from typing import Dict

class DataProcessor:

    def process_text_input(self, text: str) -> Dict[str, str]:
        """
        Handles plain text input.
        """
        if not text or not text.strip():
            raise ValueError("Text input is empty.")

        return {
            "source_type": "text",
            "raw_content": text.strip()
        }

    def process_pdf(self, pdf_file) -> Dict[str, str]:
        """
        Extracts text from a PDF.
        Supports:
        - Local file path string
        - Gradio NamedString object
        - Gradio dict format
        """
        try:
            # Case 1: Local file path string
            if isinstance(pdf_file, str):
                pdf_path = pdf_file

            # Case 2: Gradio NamedString object
            elif hasattr(pdf_file, "name"):
                pdf_path = pdf_file.name

            # Case 3: Gradio dict format
            elif isinstance(pdf_file, dict) and "name" in pdf_file:
                pdf_path = pdf_file["name"]

            else:
                raise ValueError("Invalid PDF input format.")

            # Open PDF using PyMuPDF
            doc = fitz.open(pdf_path)
            text = ""

            for page in doc:
                text += page.get_text() # type: ignore

            if not text.strip():
                raise ValueError("PDF contains no readable text.")

            return {
                "source_type": "pdf",
                "raw_content": text.strip()
            }

        except Exception as e:
            raise ValueError(f"Failed to read PDF: {str(e)}")