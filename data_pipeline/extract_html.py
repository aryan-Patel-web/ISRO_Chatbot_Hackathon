# data_pipeline/extract_html.py

from bs4 import BeautifulSoup
import os

def extract_text_from_html(html_file):
    with open(html_file, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    return text

def process_all_html():
    input_dir = "assets/html"
    output_dir = "assets/texts"
    os.makedirs(output_dir, exist_ok=True)

    for file in os.listdir(input_dir):
        if file.endswith(".html"):
            path = os.path.join(input_dir, file)
            text = extract_text_from_html(path)
            out_path = os.path.join(output_dir, file.replace(".html", ".txt"))
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)

if __name__ == "__main__":
    process_all_html()
