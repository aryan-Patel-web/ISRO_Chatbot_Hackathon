# chatbot/rag_chain.py

import os
from langchain.chains import ConversationalRetrievalChain
from langchain_groq import ChatGroq
from chatbot.memory_chain import create_memory
from embeddings_pipeline.vectorstore import vectorstore as get_vectorstore

def build_rag_chain():
    # Initialize Groq LLM
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model="gemma2-9b-it",
        temperature=0
    )
    memory = create_memory()

    vectorstore = get_vectorstore()
    retriever = vectorstore.as_retriever()

    chain = ConversationalRetrievalChain.from_llm(
        llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,
        verbose=False
    )
    return chain
