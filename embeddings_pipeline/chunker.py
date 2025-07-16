# embeddings_pipeline/chunker.py

from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def chunk_text_files(input_dir="assets/texts"):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = []
    for file in os.listdir(input_dir):
        path = os.path.join(input_dir, file)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        file_chunks = splitter.split_text(text)
        for chunk in file_chunks:
            chunks.append({"text": chunk, "source": file})
    return chunks

if __name__ == "__main__":
    all_chunks = chunk_text_files()
    print(f"Chunks created: {len(all_chunks)}")
