# embeddings_pipeline/embedder.py

from langchain.embeddings import OpenAIEmbeddings
import os

def embed_texts(chunks):
    embedder = OpenAIEmbeddings()
    embeddings = []
    for chunk in chunks:
        vector = embedder.embed_query(chunk["text"])
        embeddings.append({
            "vector": vector,
            "text": chunk["text"],
            "source": chunk["source"]
        })
    return embeddings
