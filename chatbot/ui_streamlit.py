# chatbot/ui_streamlit.py

import streamlit as st
from chatbot.rag_chain import build_rag_chain

st.set_page_config(page_title="ISRO Chatbot")
st.title("🚀 ISRO Chatbot (Powered by Gemma 2 9B IT LLM via Groq)")

rag_chain = build_rag_chain()

if "history" not in st.session_state:
    st.session_state.history = []

query = st.chat_input("Ask anything about ISRO…")
if query:
    result = rag_chain({"question": query})
    answer = result["answer"]
    st.session_state.history.append((query, answer))

for q, a in st.session_state.history:
    st.write(f"**You:** {q}")
    st.write(f"**ISROBot:** {a} 👍")
