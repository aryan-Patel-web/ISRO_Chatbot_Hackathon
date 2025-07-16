# data_pipeline/extract_pdf.py

import os
import fitz

def extract_text_from_pdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text()
    return text

def process_all_pdfs():
    input_dir = "assets/pdfs"
    output_dir = "assets/texts"
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.endswith(".pdf"):
            path = os.path.join(input_dir, file)
            text = extract_text_from_pdf(path)
            out_path = os.path.join(output_dir, file.replace(".pdf", ".txt"))
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)

if __name__ == "__main__":
    process_all_pdfs()
