import os
import re
import glob
from dotenv import load_dotenv
import streamlit as st

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.tools import WikipediaQueryRun, ArxivQueryRun
from langchain.agents import Tool
from langchain_community.utilities import WikipediaAPIWrapper, ArxivAPIWrapper
from langchain_community.vectorstores.astradb import AstraDB

import requests
from bs4 import BeautifulSoup

# Load environment
load_dotenv()

# Read keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
ASTRA_DB_API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
ASTRA_DB_KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE")

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Initialize Groq LLM backend
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="gemma-2b-it",
    temperature=0.2
)

# External tools
wiki_tool = Tool.from_function(
    name="Wikipedia",
    func=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),
    description="Look up factual info."
)

arxiv_tool = Tool.from_function(
    name="Arxiv",
    func=ArxivQueryRun(api_wrapper=ArxivAPIWrapper()),
    description="Look up research papers."
)

def scrape_url(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        return text
    except Exception as e:
        return f"Scraping failed: {e}"

# Prompts
ENG_PROMPT = (
    "You are an aerospace engineering expert. Provide highly technical, precise answers. "
    "Context:\n{context}\n\nChat History:\n{chat_history}\n\nQuestion:\n{question}"
)

STUDENT_PROMPT = (
    "You are a teacher explaining space tech to students. Use simple language and analogies. "
    "Context:\n{context}\n\nChat History:\n{chat_history}\n\nQuestion:\n{question}"
)

st.title("ISRO AI Knowledge Assistant")

session_id = st.text_input("Session ID", value="default_session")

# =============== Load PDFs from folder ==============
pdf_folder_path = "./pdfread"
folder_documents = []

if os.path.exists(pdf_folder_path):
    pdf_files = glob.glob(os.path.join(pdf_folder_path, "*.pdf"))
    for path in pdf_files:
        loader = PyPDFLoader(path)
        docs = loader.load()
        folder_documents.extend(docs)

# =============== Handle Uploaded PDFs ===============
uploaded_files = st.file_uploader("Upload PDF documents", type="pdf", accept_multiple_files=True)

uploaded_documents = []
if uploaded_files:
    for uploaded_file in uploaded_files:
        temppath = "./temp.pdf"
        with open(temppath, "wb") as f:
            f.write(uploaded_file.getvalue())
        loader = PyPDFLoader(temppath)
        docs = loader.load()
        uploaded_documents.extend(docs)

# =============== Combine all documents ==============
all_documents = folder_documents + uploaded_documents

if all_documents:
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=500)
    splits = text_splitter.split_documents(all_documents)

    # Vector DB in Astra
    vectorstore = AstraDB.from_documents(
        documents=splits,
        embedding=embeddings,
        collection_name="isro_knowledge_base",
        api_endpoint=ASTRA_DB_API_ENDPOINT,
        token=ASTRA_DB_APPLICATION_TOKEN,
        namespace=ASTRA_DB_KEYSPACE
    )

    retriever = vectorstore.as_retriever()

    # Create history-aware retriever
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question, "
        "formulate a standalone question if necessary."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_q_prompt
    )

    qa_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_prompt}"),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt_template)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # Session management
    if "store" not in st.session_state:
        st.session_state.store = {}

    def get_session_history(session: str) -> BaseChatMessageHistory:
        if session not in st.session_state.store:
            st.session_state.store[session] = ChatMessageHistory()
        return st.session_state.store[session]

    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    user_question = st.text_input("Your question:")
    mode = st.radio("Select mode:", ["engineering", "student"])

    if user_question:
        # Check if question includes a URL
        url_match = re.search(r"(https?://\S+)", user_question)
        context = ""

        if url_match:
            url = url_match.group(1)
            st.info(f"Scraping content from URL: {url}")
            context = scrape_url(url)
        else:
            # Run RAG chain
            session_history = get_session_history(session_id)
            rag_response = conversational_rag_chain.invoke(
                {"input": user_question},
                config={"configurable": {"session_id": session_id}}
            )
            context = rag_response["answer"]

            # Check if RAG found anything
            if context.strip().lower() in ["", "i don't know"]:
                try:
                    wiki_ans = wiki_tool.run(user_question)
                    if wiki_ans:
                        context = wiki_ans
                except:
                    pass
                try:
                    arxiv_ans = arxiv_tool.run(user_question)
                    if arxiv_ans:
                        context = arxiv_ans
                except:
                    pass

        # Construct prompt
        system_prompt = ENG_PROMPT if mode == "engineering" else STUDENT_PROMPT
        session_history = get_session_history(session_id)
        final_prompt = system_prompt.format(
            context=context,
            question=user_question,
            chat_history=session_history.messages
        )

        final_answer = llm.invoke(final_prompt).content
        st.write("Assistant:", final_answer)
        st.write("Chat History:", session_history.messages)

else:
    st.info("Upload PDFs or add PDFs to the `pdfread` folder to begin.")
