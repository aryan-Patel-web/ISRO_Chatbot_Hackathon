# embeddings_pipeline/vectorstore.py

from langchain.vectorstores import AstraDB
from langchain.embeddings import OpenAIEmbeddings
from embeddings_pipeline.chunker import chunk_text_files

def store_in_astradb():
    embedding = OpenAIEmbeddings()

    vectorstore = AstraDB(
        embedding=embedding,
        token=os.getenv("ASTRA_DB_APPLICATION_TOKEN"),
        api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
        collection_name="isro_docs"
    )

    chunks = chunk_text_files()
    texts = [c["text"] for c in chunks]

    vectorstore.add_texts(texts)
    print("Data uploaded to AstraDB.")

if __name__ == "__main__":
    store_in_astradb()
